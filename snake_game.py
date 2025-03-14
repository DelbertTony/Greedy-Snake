import pygame
import random
import sys
import json
import os

# 初始化 Pygame
pygame.init()

# 定义颜色
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)

# 游戏设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# 创建窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('贪吃蛇')

class Obstacle:
    def __init__(self):
        self.positions = []
        self.color = GRAY
        
    def generate(self, snake_positions, food_position):
        self.positions = []
        # 生成5个随机障碍物
        for _ in range(5):
            while True:
                pos = (random.randint(0, GRID_WIDTH-1),
                      random.randint(0, GRID_HEIGHT-1))
                if (pos not in snake_positions and 
                    pos not in self.positions and 
                    pos != food_position):
                    self.positions.append(pos)
                    break

class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN
        self.score = 0
        self.speed = 10  # 初始速度

    def get_head_position(self):
        return self.positions[0]

    def update(self, obstacles):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        
        # 检查是否撞到自己或障碍物
        if (new in self.positions[2:] or 
            new in obstacles.positions):
            return False
        
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True

    def reset(self):
        self.length = 1
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0
        self.speed = 10

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH-1),
                        random.randint(0, GRID_HEIGHT-1))

# 方向常量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Game:
    def __init__(self):
        self.high_score = self.load_high_score()
        self.state = "MENU"
        # 简化字体设置
        try:
            if sys.platform.startswith('win'):
                self.font = pygame.font.SysFont('simhei', 48)  # 使用黑体
            else:
                self.font = pygame.font.SysFont('arial', 48)
        except:
            print("警告：未找到合适的字体")
            self.font = pygame.font.Font(None, 48)
        
        # 创建一个小号字体用于显示分数
        self.small_font = pygame.font.SysFont('simhei', 36) if sys.platform.startswith('win') else pygame.font.SysFont('arial', 36)

    def load_high_score(self):
        try:
            with open('high_score.json', 'r') as f:
                return json.load(f)['high_score']
        except:
            return 0
            
    def save_high_score(self, score):
        if score > self.high_score:
            self.high_score = score
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': score}, f)

    def draw_menu(self):
        screen.fill(BLACK)
        title = self.font.render('贪吃蛇', True, GREEN)
        start = self.font.render('按空格开始', True, WHITE)
        high_score = self.font.render(f'最高分: {self.high_score}', True, BLUE)
        
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
        screen.blit(start, (WINDOW_WIDTH//2 - start.get_width()//2, 300))
        screen.blit(high_score, (WINDOW_WIDTH//2 - high_score.get_width()//2, 400))

    def draw_game_over(self, score):
        screen.fill(BLACK)
        # 使用类中定义的字体
        game_over = self.font.render('游戏结束', True, RED)
        score_text = self.font.render(f'得分: {score}', True, WHITE)
        restart = self.font.render('按空格重新开始', True, GREEN)
        
        screen.blit(game_over, (WINDOW_WIDTH//2 - game_over.get_width()//2, 200))
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 300))
        screen.blit(restart, (WINDOW_WIDTH//2 - restart.get_width()//2, 400))

def main():
    clock = pygame.time.Clock()
    game = Game()
    snake = Snake()
    food = Food()
    obstacles = Obstacle()
    
    while True:
        if game.state == "MENU":
            game.draw_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game.state = "PLAYING"
                        snake.reset()
                        food.randomize_position()
                        obstacles.generate(snake.positions, food.position)

        elif game.state == "PLAYING":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and snake.direction != DOWN:
                        snake.direction = UP
                    elif event.key == pygame.K_DOWN and snake.direction != UP:
                        snake.direction = DOWN
                    elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                        snake.direction = LEFT
                    elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                        snake.direction = RIGHT

            if not snake.update(obstacles):
                game.save_high_score(snake.score)
                game.state = "GAME_OVER"
                continue

            if snake.get_head_position() == food.position:
                snake.length += 1
                snake.score += 1
                food.randomize_position()
                if snake.score % 5 == 0:
                    snake.speed = min(snake.speed + 2, 25)

            screen.fill(BLACK)
            
            # 绘制障碍物
            for pos in obstacles.positions:
                pygame.draw.rect(screen, obstacles.color,
                               (pos[0] * GRID_SIZE,
                                pos[1] * GRID_SIZE,
                                GRID_SIZE, GRID_SIZE))
            
            # 绘制食物和蛇
            pygame.draw.rect(screen, food.color,
                           (food.position[0] * GRID_SIZE,
                            food.position[1] * GRID_SIZE,
                            GRID_SIZE, GRID_SIZE))
            
            for pos in snake.positions:
                pygame.draw.rect(screen, snake.color,
                               (pos[0] * GRID_SIZE,
                                pos[1] * GRID_SIZE,
                                GRID_SIZE-1, GRID_SIZE-1))

            # 使用小号字体显示分数
            score_text = game.small_font.render(f'得分: {snake.score} 最高分: {game.high_score}', True, WHITE)
            screen.blit(score_text, (10, 10))

        elif game.state == "GAME_OVER":
            game.draw_game_over(snake.score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game.state = "MENU"

        pygame.display.update()
        clock.tick(snake.speed)

if __name__ == '__main__':
    main() 