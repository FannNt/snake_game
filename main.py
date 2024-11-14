import pygame
import random
import sys
import os
from enum import Enum

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Constants
CELL_SIZE = 30
GRID_WIDTH = 20
GRID_HEIGHT = 15
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

# Create assets directory
if not os.path.exists('assets'):
    os.makedirs('assets')

# Function to create different fruit images
def create_fruit_images():
    fruits = {
        'apple': {'color': (255, 0, 0), 'stem_color': (101, 67, 33), 'leaf_color': (50, 205, 50)},
        'orange': {'color': (255, 165, 0), 'stem_color': (101, 67, 33), 'leaf_color': (50, 205, 50)},
        'blueberry': {'color': (65, 105, 225), 'stem_color': (101, 67, 33), 'leaf_color': (50, 205, 50)},
        'strawberry': {'color': (220, 20, 60), 'stem_color': (101, 67, 33), 'leaf_color': (50, 205, 50)},
        'grape': {'color': (147, 112, 219), 'stem_color': (101, 67, 33), 'leaf_color': (50, 205, 50)}
    }
    
    fruit_images = {}
    
    for fruit_name, colors in fruits.items():
        image_path = f'assets/{fruit_name}.png'
        if not os.path.exists(image_path):
            surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            
            # Draw base fruit shape
            if fruit_name == 'grape':
                # Cluster of small circles for grape
                for i in range(3):
                    for j in range(3):
                        pygame.draw.circle(surface, colors['color'],
                                        (10 + i * 10, 10 + j * 10), 5)
            elif fruit_name == 'strawberry':
                # Heart-like shape for strawberry
                pygame.draw.ellipse(surface, colors['color'],
                                 (5, 10, 20, 25))
                # Add seeds
                for _ in range(8):
                    x = random.randint(8, 22)
                    y = random.randint(13, 30)
                    pygame.draw.circle(surface, (255, 255, 200), (x, y), 1)
            else:
                # Regular circle for other fruits
                pygame.draw.circle(surface, colors['color'],
                                (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2 - 2)
            
            # Add stem and leaf to all fruits
            pygame.draw.ellipse(surface, colors['stem_color'],
                             (CELL_SIZE//2 - 2, 5, 4, 8))
            pygame.draw.ellipse(surface, colors['leaf_color'],
                             (CELL_SIZE//2 - 4, 3, 8, 6))
            
            pygame.image.save(surface, image_path)
        
        fruit_images[fruit_name] = pygame.image.load(image_path)
    
    return fruit_images

# Create and save eating sound
def create_eating_sound():
    sound_path = 'assets/eating.wav'
    if not os.path.exists(sound_path):
        pygame.sndarray.save(pygame.sndarray.make_sound(
            pygame.Surface((44100,)).get_buffer().raw), sound_path)
    return pygame.mixer.Sound(sound_path)

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class Food:
    def __init__(self, pos, fruit_type, image):
        self.pos = pos
        self.fruit_type = fruit_type
        self.image = image
        self.points = {
            'apple': 10,
            'orange': 15,
            'blueberry': 20,
            'strawberry': 25,
            'grape': 30
        }
    
    def get_points(self):
        return self.points[self.fruit_type]

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.direction = Direction.RIGHT
        self.body = [(GRID_WIDTH // 4, GRID_HEIGHT // 2)]
        self.growth_pending = False
    
    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
        
        if not self.growth_pending:
            self.body.pop()
        else:
            self.growth_pending = False
        
        self.body.insert(0, new_head)
    
    def grow(self):
        self.growth_pending = True
    
    def check_collision(self):
        return self.body[0] in self.body[1:]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Load assets
        self.fruit_images = create_fruit_images()
        self.eat_sound = create_eating_sound()
        
        self.reset()
    
    def reset(self):
        self.snake = Snake()
        self.spawn_food()
        self.score = 0
        self.game_over = False
    
    def spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH-1), 
                  random.randint(0, GRID_HEIGHT-1))
            if pos not in self.snake.body:
                break
        
        fruit_type = random.choice(list(self.fruit_images.keys()))
        self.food = Food(pos, fruit_type, self.fruit_images[fruit_type])
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
        
        keys = pygame.key.get_pressed()
        if not self.game_over:
            if keys[pygame.K_UP] and self.snake.direction != Direction.DOWN:
                self.snake.direction = Direction.UP
            elif keys[pygame.K_DOWN] and self.snake.direction != Direction.UP:
                self.snake.direction = Direction.DOWN
            elif keys[pygame.K_LEFT] and self.snake.direction != Direction.RIGHT:
                self.snake.direction = Direction.LEFT
            elif keys[pygame.K_RIGHT] and self.snake.direction != Direction.LEFT:
                self.snake.direction = Direction.RIGHT
    
    def update(self):
        if self.game_over:
            return
        
        self.snake.move()
        
        # Check if snake ate food
        if self.snake.body[0] == self.food.pos:
            self.eat_sound.play()
            self.snake.grow()
            self.score += self.food.get_points()
            self.spawn_food()
        
        # Check for collision with self
        if self.snake.check_collision():
            self.game_over = True
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw snake
        for segment in self.snake.body:
            x, y = segment
            pygame.draw.rect(self.screen, GREEN,
                           (x * CELL_SIZE, y * CELL_SIZE,
                            CELL_SIZE - 1, CELL_SIZE - 1))
        
        # Draw food
        self.screen.blit(self.food.image,
                        (self.food.pos[0] * CELL_SIZE, 
                         self.food.pos[1] * CELL_SIZE))
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw current fruit type and points
        fruit_text = self.font.render(
            f'Fruit: {self.food.fruit_type.title()} ({self.food.get_points()} pts)',
            True, WHITE)
        self.screen.blit(fruit_text, (WIDTH - fruit_text.get_width() - 10, 10))
        
        # Draw game over message
        if self.game_over:
            game_over_text = self.font.render('Game Over! Press R to restart',
                                            True, WHITE)
            text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()