import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)

# Initialize pygame
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hill Climbing Visualization")
FONT = pygame.font.SysFont('Arial', 18)


class Board:
    def __init__(self, rows, cols, square_size):
        self.rows = rows
        self.cols = cols
        self.square_size = square_size
        self.start = None
        self.goal = None
        self.barriers = set()
        self.path = []
        self.visited = []

    def set_start_goal(self):
        self.start = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
        self.goal = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
        while self.goal == self.start:
            self.goal = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))

    def draw(self, win, current_pos):
        win.fill(WHITE)
        # Draw grid
        for row in range(self.rows):
            for col in range(self.cols):
                pygame.draw.rect(win, BLACK, (col * self.square_size, row * self.square_size, self.square_size, self.square_size), 1)

        # Draw start and goal
        pygame.draw.rect(win, GREEN, (self.start[1] * self.square_size, self.start[0] * self.square_size, self.square_size, self.square_size))
        pygame.draw.rect(win, RED, (self.goal[1] * self.square_size, self.goal[0] * self.square_size, self.square_size, self.square_size))

        # Draw barriers
        for barrier in self.barriers:
            pygame.draw.rect(win, DARK_GRAY, (barrier[1] * self.square_size, barrier[0] * self.square_size, self.square_size, self.square_size))

        # Draw visited cells and arrows
        for i in range(len(self.visited)):
            prev_pos = self.visited[i]
            # If the current position is the goal, highlight the path in dark green
            color = (0, 100, 0) if prev_pos == self.goal else (0, 150, 0)
            pygame.draw.rect(win, color, (prev_pos[1] * self.square_size, prev_pos[0] * self.square_size, self.square_size, self.square_size))
            
            # Draw arrows to show the movement direction, but only if there's a next step
            if i < len(self.visited) - 1:
                next_pos = self.visited[i + 1]
                self.draw_arrow(win, prev_pos, next_pos)


        # Draw current position
        pygame.draw.rect(win, BLUE, (current_pos[1] * self.square_size, current_pos[0] * self.square_size, self.square_size, self.square_size))

    def draw_arrow(self, win, start, end):
        # Calculate arrow direction
        start_pos = (start[1] * self.square_size + self.square_size // 2, start[0] * self.square_size + self.square_size // 2)
        end_pos = (end[1] * self.square_size + self.square_size // 2, end[0] * self.square_size + self.square_size // 2)
        pygame.draw.line(win, GREEN, start_pos, end_pos, 3)
        angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
        arrow_head = [(end_pos[0] - 10 * math.cos(angle - math.pi / 6), end_pos[1] - 10 * math.sin(angle - math.pi / 6)),
                      (end_pos[0] - 10 * math.cos(angle + math.pi / 6), end_pos[1] - 10 * math.sin(angle + math.pi / 6))]
        pygame.draw.polygon(win, GREEN, [end_pos, *arrow_head])

    def draw_text(self, win, text, pos, color=BLACK):
        text_surface = FONT.render(text, True, color)
        win.blit(text_surface, pos)

    def add_barriers(self, count):
        while len(self.barriers) < count:
            barrier = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
            if barrier != self.start and barrier != self.goal:
                self.barriers.add(barrier)

    def show_heuristic_values(self, win, current_pos, pathfinder):
        # Display heuristic values and coordinates of neighboring cells
        if current_pos == self.goal:
            return  # Don't show heuristic values if at the goal

        neighbors = pathfinder.get_neighbors(current_pos)
        for neighbor in neighbors:
            # Ensure the neighbor is not a barrier or a visited cell
            if neighbor not in self.barriers and neighbor not in self.visited:
                distance = pathfinder.chebyshev_distance(neighbor[0], neighbor[1], self.goal[0], self.goal[1])
                pygame.draw.rect(win, GRAY, (neighbor[1] * self.square_size, neighbor[0] * self.square_size, self.square_size, self.square_size))
                self.draw_text(win, f"{neighbor}", (neighbor[1] * self.square_size + 5, neighbor[0] * self.square_size + 5), BLACK)
                self.draw_text(win, f"H:{distance}", (neighbor[1] * self.square_size + 5, neighbor[0] * self.square_size + 25), BLACK)

        # Display heuristic value of the current position
        current_distance = pathfinder.chebyshev_distance(current_pos[0], current_pos[1], self.goal[0], self.goal[1])
        self.draw_text(win, f"{current_pos}", (current_pos[1] * self.square_size + 5, current_pos[0] * self.square_size + 5), WHITE)
        self.draw_text(win, f"H:{current_distance}", (current_pos[1] * self.square_size + 5, current_pos[0] * self.square_size + 25), WHITE)


class Pathfinder:
    def __init__(self, board):
        self.board = board

    @staticmethod
    def chebyshev_distance(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board.rows and 0 <= ny < self.board.cols:
                neighbors.append((nx, ny))
        return neighbors

    def hill_climbing(self, max_attempts=100):
        attempts = 0
        while attempts < max_attempts:
            current = self.board.start
            path = [current]
            visited = set()
            visited.add(current)

            while current != self.board.goal:
                neighbors = self.get_neighbors(current)
                best_moves = []
                min_distance = float('inf')

                for neighbor in neighbors:
                    if neighbor not in self.board.barriers and neighbor not in visited:
                        distance = self.chebyshev_distance(neighbor[0], neighbor[1], self.board.goal[0], self.board.goal[1])
                        if distance < min_distance:
                            min_distance = distance
                            best_moves = [neighbor]
                        elif distance == min_distance:
                            best_moves.append(neighbor)

                if not best_moves:
                    break

                current = random.choice(best_moves)
                path.append(current)
                visited.add(current)

            if current == self.board.goal:
                self.board.path = path
                return path

            attempts += 1

        print("Failed to find a path after", max_attempts, "attempts")
        self.board.path = path
        return path


class Game:
    def __init__(self):
        self.board = Board(ROWS, COLS, SQUARE_SIZE)
        self.pathfinder = Pathfinder(self.board)
        self.step_index = 0

    def run(self):
        run = True
        clock = pygame.time.Clock()

        # Initialize start, goal, and barriers
        self.board.set_start_goal()
        self.board.add_barriers(10)
        self.pathfinder.hill_climbing()

        while run:
            clock.tick(10)
            current_pos = self.board.path[min(self.step_index, len(self.board.path) - 1)]
            next_pos = self.board.path[self.step_index + 1] if self.step_index < len(self.board.path) - 1 else None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        if self.step_index < len(self.board.path) - 1:
                            self.board.visited.append(current_pos)
                            self.step_index += 1
                    elif event.key == pygame.K_LEFT:
                        if self.step_index > 0:
                            self.step_index -= 1
                            self.board.visited.pop()

            self.board.draw(WIN, current_pos)
            self.board.show_heuristic_values(WIN, current_pos, self.pathfinder)
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
