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

# 添加主题颜色
LIGHT_THEME = {
    'background': (240, 240, 240),
    'grid': (200, 200, 200),
    'text': (60, 60, 60),
    'snake_head': (0, 180, 0),
    'snake_body': (0, 160, 0),
    'food': (200, 50, 50),
    'obstacle': (150, 150, 150)
}

DARK_THEME = {
    'background': (0, 0, 0),
    'grid': (40, 40, 40),
    'text': (255, 255, 255),
    'snake_head': (0, 200, 0),
    'snake_body': (0, 180, 0),
    'food': (200, 50, 50),
    'obstacle': (100, 100, 100)
}

# 游戏设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# 创建窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('贪吃蛇')

# 添加新的颜色常量
GRID_COLOR = (40, 40, 40)  # 深色网格线
SNAKE_HEAD_COLOR = (0, 200, 0)  # 蛇头颜色
SNAKE_BODY_COLOR = (0, 180, 0)  # 蛇身颜色
FOOD_COLOR = (200, 50, 50)  # 更鲜艳的食物颜色
OBSTACLE_COLOR = (100, 100, 100)  # 柔和的障碍物颜色

# 添加新的常量
DEFAULT_SPEED = 8  # 默认速度
MIN_SPEED = 4  # 最小速度
MAX_SPEED = 15  # 最大速度
MAX_LEADERBOARD_ENTRIES = 10  # 排行榜最大记录数

def get_resource_path(relative_path):
    """ 获取资源文件的绝对路径 """
    try:
        # PyInstaller 创建临时文件夹 _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

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
        self.direction_queue = []  # 改用方向队列存储多个输入
        self.last_update_time = 0  # 用于控制更新频率

    def get_head_position(self):
        return self.positions[0]

    def handle_input(self, new_direction):
        # 检查新方向是否与当前方向或最后一个队列方向相反
        current_dir = self.direction_queue[-1] if self.direction_queue else self.direction
        if ((new_direction[0] * -1, new_direction[1] * -1) != current_dir and
            (new_direction[0], new_direction[1]) != current_dir):
            # 限制队列长度为2，保留最新的输入
            if len(self.direction_queue) < 2:
                self.direction_queue.append(new_direction)

    def update(self, obstacles):
        current_time = pygame.time.get_ticks()
        # 确保有足够的时间间隔再更新方向
        if current_time - self.last_update_time > 1000 // self.speed:
            # 处理方向队列
            if self.direction_queue:
                self.direction = self.direction_queue.pop(0)
            
            cur = self.get_head_position()
            x, y = self.direction
            new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
            
            if (new in self.positions[2:] or new in obstacles.positions):
                return False
            
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()
            
            self.last_update_time = current_time
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
        self.leaderboard = self.load_leaderboard()
        self.state = "MENU"  # MENU, SETTINGS, PLAYING, PAUSED, GAME_OVER, INPUT_NAME
        self.current_speed = DEFAULT_SPEED
        self.player_name = ""
        self.theme = DARK_THEME  # 添加主题设置
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
            path = get_resource_path('high_score.json')
            with open(path, 'r') as f:
                return json.load(f)['high_score']
        except:
            return 0
            
    def save_high_score(self, score):
        if score > self.high_score:
            self.high_score = score
            path = get_resource_path('high_score.json')
            with open(path, 'w') as f:
                json.dump({'high_score': score}, f)

    def load_leaderboard(self):
        try:
            path = get_resource_path('leaderboard.json')
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return []

    def save_leaderboard(self, name, score):
        # 添加速度信息到记录中
        new_entry = {
            "name": name, 
            "score": score,
            "speed": self.current_speed  # 添加速度信息
        }
        self.leaderboard.append(new_entry)
        
        # 按速度分组，每个速度保留前10名
        speed_groups = {}
        for entry in self.leaderboard:
            speed = entry["speed"]
            if speed not in speed_groups:
                speed_groups[speed] = []
            speed_groups[speed].append(entry)
        
        # 对每个速度组内的记录按分数排序
        new_leaderboard = []
        for speed in speed_groups:
            speed_groups[speed].sort(key=lambda x: x["score"], reverse=True)
            new_leaderboard.extend(speed_groups[speed][:MAX_LEADERBOARD_ENTRIES])
        
        self.leaderboard = new_leaderboard
        path = get_resource_path('leaderboard.json')
        with open(path, 'w') as f:
            json.dump(self.leaderboard, f)

    def draw_menu(self):
        screen.fill(BLACK)
        self.draw_grid()
        
        title = self.font.render('贪吃蛇', True, GREEN)
        start = self.font.render('1. 开始游戏', True, WHITE)
        settings = self.font.render('2. 设置', True, WHITE)
        leaderboard = self.font.render('3. 排行榜', True, WHITE)
        quit_text = self.font.render('4. 退出', True, WHITE)
        
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        screen.blit(start, (WINDOW_WIDTH//2 - start.get_width()//2, 200))
        screen.blit(settings, (WINDOW_WIDTH//2 - settings.get_width()//2, 270))
        screen.blit(leaderboard, (WINDOW_WIDTH//2 - leaderboard.get_width()//2, 340))
        screen.blit(quit_text, (WINDOW_WIDTH//2 - quit_text.get_width()//2, 410))

    def draw_settings(self):
        screen.fill(self.theme['background'])
        self.draw_grid()
        
        title = self.font.render('设置', True, self.theme['text'])
        speed_text = self.font.render(f'速度: {self.current_speed}', True, self.theme['text'])
        theme_text = self.font.render(f'主题: {"暗色" if self.theme == DARK_THEME else "亮色"}', True, self.theme['text'])
        controls = self.small_font.render('左右键调速度，T键切换主题，ESC返回', True, self.theme['text'])
        
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
        screen.blit(speed_text, (WINDOW_WIDTH//2 - speed_text.get_width()//2, 250))
        screen.blit(theme_text, (WINDOW_WIDTH//2 - theme_text.get_width()//2, 350))
        screen.blit(controls, (WINDOW_WIDTH//2 - controls.get_width()//2, 450))

    def draw_leaderboard(self):
        screen.fill(self.theme['background'])
        self.draw_grid()
        
        title = self.font.render('排行榜', True, self.theme['text'])
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))
        
        # 按速度分组显示排行榜
        speed_groups = {}
        for entry in self.leaderboard:
            speed = entry["speed"]
            if speed not in speed_groups:
                speed_groups[speed] = []
            speed_groups[speed].append(entry)
        
        y_pos = 120
        for speed in sorted(speed_groups.keys()):
            # 显示速度标题
            speed_text = self.small_font.render(f"速度 {speed}:", True, self.theme['text'])
            screen.blit(speed_text, (50, y_pos))
            y_pos += 30
            
            # 显示该速度下的前10名
            for i, entry in enumerate(sorted(speed_groups[speed], key=lambda x: x["score"], reverse=True)[:10]):
                text = self.small_font.render(
                    f"{i+1}. {entry['name']}: {entry['score']}", 
                    True, 
                    self.theme['text']
                )
                screen.blit(text, (80, y_pos))
                y_pos += 25
            
            y_pos += 15  # 不同速度组之间添加间距
            
            # 如果超出屏幕范围，停止显示
            if y_pos > WINDOW_HEIGHT - 60:
                break
        
        back = self.small_font.render('按ESC返回', True, self.theme['text'])
        screen.blit(back, (WINDOW_WIDTH//2 - back.get_width()//2, WINDOW_HEIGHT - 40))

    def draw_name_input(self, score):
        screen.fill(self.theme['background'])
        self.draw_grid()
        
        title = self.font.render('新高分！', True, self.theme['text'])
        score_text = self.font.render(f'得分: {score}', True, self.theme['text'])
        speed_text = self.font.render(f'速度: {self.current_speed}', True, self.theme['text'])  # 添加速度显示
        name_text = self.font.render(f'名字: {self.player_name}', True, self.theme['text'])
        hint = self.small_font.render('输入你的名字并按回车确认', True, self.theme['text'])
        
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 220))
        screen.blit(speed_text, (WINDOW_WIDTH//2 - speed_text.get_width()//2, 290))  # 显示速度
        screen.blit(name_text, (WINDOW_WIDTH//2 - name_text.get_width()//2, 360))
        screen.blit(hint, (WINDOW_WIDTH//2 - hint.get_width()//2, 430))

    def draw_game_over(self, score):
        screen.fill(BLACK)
        self.draw_grid()
        
        game_over = self.font.render('游戏结束', True, RED)
        score_text = self.font.render(f'得分: {score}', True, WHITE)
        restart = self.font.render('按空格重新开始', True, GREEN)
        
        screen.blit(game_over, (WINDOW_WIDTH//2 - game_over.get_width()//2, 200))
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 300))
        screen.blit(restart, (WINDOW_WIDTH//2 - restart.get_width()//2, 400))

    def draw_paused(self):
        # 保持游戏画面，只添加暂停提示
        pause_text = self.font.render('已暂停', True, WHITE)
        continue_text = self.small_font.render('按空格继续', True, WHITE)
        
        # 创建半透明的黑色遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, 250))
        screen.blit(continue_text, (WINDOW_WIDTH//2 - continue_text.get_width()//2, 320))

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, self.theme['grid'], (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, self.theme['grid'], (0, y), (WINDOW_WIDTH, y))

    def draw_snake(self, snake):
        for i, pos in enumerate(snake.positions):
            color = self.theme['snake_head'] if i == 0 else self.theme['snake_body']
            x = pos[0] * GRID_SIZE
            y = pos[1] * GRID_SIZE
            
            rect = pygame.Rect(x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            
            if i == 0:
                eye_offset = 4
                if snake.direction == LEFT or snake.direction == RIGHT:
                    pygame.draw.circle(screen, WHITE, (x + GRID_SIZE//2, y + eye_offset), 2)
                    pygame.draw.circle(screen, WHITE, (x + GRID_SIZE//2, y + GRID_SIZE - eye_offset), 2)
                else:
                    pygame.draw.circle(screen, WHITE, (x + eye_offset, y + GRID_SIZE//2), 2)
                    pygame.draw.circle(screen, WHITE, (x + GRID_SIZE - eye_offset, y + GRID_SIZE//2), 2)

    def draw_food(self, food):
        # 绘制食物为圆形
        x = food.position[0] * GRID_SIZE + GRID_SIZE // 2
        y = food.position[1] * GRID_SIZE + GRID_SIZE // 2
        pygame.draw.circle(screen, FOOD_COLOR, (x, y), GRID_SIZE // 2 - 2)

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
                    if event.key == pygame.K_1:
                        game.state = "PLAYING"
                        snake.reset()
                        snake.speed = game.current_speed
                        food.randomize_position()
                        obstacles.generate(snake.positions, food.position)
                    elif event.key == pygame.K_2:
                        game.state = "SETTINGS"
                    elif event.key == pygame.K_3:
                        game.state = "LEADERBOARD"
                    elif event.key == pygame.K_4:
                        pygame.quit()
                        sys.exit()

        elif game.state == "SETTINGS":
            game.draw_settings()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.state = "MENU"
                    elif event.key == pygame.K_LEFT:
                        game.current_speed = max(MIN_SPEED, game.current_speed - 1)
                    elif event.key == pygame.K_RIGHT:
                        game.current_speed = min(MAX_SPEED, game.current_speed + 1)
                    elif event.key == pygame.K_t:  # 添加主题切换
                        game.theme = LIGHT_THEME if game.theme == DARK_THEME else DARK_THEME

        elif game.state == "LEADERBOARD":
            game.draw_leaderboard()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.state = "MENU"

        elif game.state == "INPUT_NAME":
            game.draw_name_input(snake.score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and game.player_name:
                        game.save_leaderboard(game.player_name, snake.score)
                        game.player_name = ""
                        game.state = "MENU"
                    elif event.key == pygame.K_BACKSPACE:
                        game.player_name = game.player_name[:-1]
                    elif len(game.player_name) < 10:  # 限制名字长度
                        if event.unicode.isprintable():
                            game.player_name += event.unicode

        elif game.state == "PLAYING":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        snake.handle_input(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.handle_input(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.handle_input(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.handle_input(RIGHT)
                    elif event.key == pygame.K_SPACE:  # 添加暂停功能
                        game.state = "PAUSED"
                    elif event.key == pygame.K_ESCAPE:
                        game.state = "MENU"

            if not snake.update(obstacles):
                game.save_high_score(snake.score)
                game.state = "INPUT_NAME"  # 改为先输入名字
                continue

            if snake.get_head_position() == food.position:
                snake.length += 1
                snake.score += 1
                food.randomize_position()
                if snake.score % 5 == 0:
                    snake.speed = min(snake.speed + 2, 25)

            screen.fill(game.theme['background'])
            game.draw_grid()
            
            # 绘制障碍物
            for pos in obstacles.positions:
                rect = pygame.Rect(pos[0] * GRID_SIZE + 1, 
                                 pos[1] * GRID_SIZE + 1,
                                 GRID_SIZE - 2, GRID_SIZE - 2)
                pygame.draw.rect(screen, game.theme['obstacle'], rect, border_radius=3)
            
            game.draw_food(food)
            game.draw_snake(snake)

            # 修改分数显示位置和样式
            score_text = game.small_font.render(f'得分: {snake.score} 最高分: {game.high_score}', True, game.theme['text'])
            score_rect = score_text.get_rect(topright=(WINDOW_WIDTH - 10, 10))
            # 添加半透明背景
            bg_surface = pygame.Surface((score_rect.width + 20, score_rect.height + 10))
            bg_surface.fill(game.theme['background'])
            bg_surface.set_alpha(200)
            screen.blit(bg_surface, (score_rect.x - 10, score_rect.y - 5))
            screen.blit(score_text, score_rect)

        elif game.state == "PAUSED":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game.state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        game.state = "MENU"
            
            # 绘制暂停界面
            game.draw_paused()

        elif game.state == "GAME_OVER":
            screen.fill(BLACK)
            game.draw_grid()  # 在游戏结束界面也显示网格
            game.draw_game_over(snake.score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game.state = "MENU"

        pygame.display.update()
        if game.state == "PLAYING":
            clock.tick(60)  # 保持60FPS的更新率，移动速度由Snake类控制
        else:
            clock.tick(60)

if __name__ == '__main__':
    main() 