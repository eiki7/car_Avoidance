import pygame
import numpy as np
import matplotlib.pyplot as plt

# Pygameの初期化
pygame.init()

# ウィンドウサイズ
WIDTH, HEIGHT = 800, 600
LANE_WIDTH = WIDTH // 4
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Vehicle Obstacle Avoidance")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (169, 169, 169)

# 車両のクラス
class Vehicle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.color = color
        self.vel = 5
        self.sensor_range = 100
        self.path = []
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        self.draw_sensors(win)
        self.path.append((self.x, self.y))
    
    def move(self, direction):
        if direction == "UP" and self.y - self.vel > 0:
            self.y -= self.vel
        elif direction == "DOWN" and self.y + self.vel + self.height < HEIGHT:
            self.y += self.vel
        elif direction == "LEFT" and self.x - self.vel > 0:
            self.x -= self.vel
        elif direction == "RIGHT" and self.x + self.vel + self.width < WIDTH:
            self.x += self.vel
    
    def draw_sensors(self, win):
        # 前方センサー
        pygame.draw.line(win, BLUE, (self.x + self.width//2, self.y), 
                         (self.x + self.width//2, max(0, self.y - self.sensor_range)), 2)
        # 左前方センサー
        pygame.draw.line(win, BLUE, (self.x, self.y), 
                         (max(0, self.x - self.sensor_range), max(0, self.y - self.sensor_range)), 2)
        # 右前方センサー
        pygame.draw.line(win, BLUE, (self.x + self.width, self.y), 
                         (min(WIDTH, self.x + self.width + self.sensor_range), max(0, self.y - self.sensor_range)), 2)
        # 左センサー
        pygame.draw.line(win, BLUE, (self.x, self.y + self.height//2), 
                         (max(0, self.x - self.sensor_range), self.y + self.height//2), 2)
        # 右センサー
        pygame.draw.line(win, BLUE, (self.x + self.width, self.y + self.height//2), 
                         (min(WIDTH, self.x + self.width + self.sensor_range), self.y + self.height//2), 2)
    
    def detect_obstacles(self, obstacles):
        front_sensor = False
        left_front_sensor = False
        right_front_sensor = False
        left_sensor = False
        right_sensor = False
        for obstacle in obstacles:
            if self.x < obstacle.x + obstacle.width and self.x + self.width > obstacle.x:
                if self.y - self.sensor_range < obstacle.y + obstacle.height and self.y > obstacle.y:
                    front_sensor = True
            if self.y - self.sensor_range < obstacle.y + obstacle.height and self.y > obstacle.y:
                if self.x - self.sensor_range < obstacle.x + obstacle.width and self.x > obstacle.x:
                    left_front_sensor = True
                if self.x + self.width + self.sensor_range > obstacle.x and self.x + self.width < obstacle.x + obstacle.width:
                    right_front_sensor = True
            if self.y < obstacle.y + obstacle.height and self.y + self.height > obstacle.y:
                if self.x - self.sensor_range < obstacle.x + obstacle.width and self.x > obstacle.x:
                    left_sensor = True
                if self.x + self.width + self.sensor_range > obstacle.x and self.x + self.width < obstacle.x + obstacle.width:
                    right_sensor = True
        return front_sensor, left_front_sensor, right_front_sensor, left_sensor, right_sensor

# 障害物のクラス
class Obstacle:
    def __init__(self, x, y, width, height, vel_x=0, vel_y=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = RED
        self.vel_x = vel_x
        self.vel_y = vel_y
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
    
    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y
        if self.x < 0 or self.x + self.width > WIDTH:
            self.vel_x = -self.vel_x
        if self.y < 0 or self.y + self.height > HEIGHT:
            self.vel_y = -self.vel_y

# 自動運転アルゴリズム
def autonomous_drive(vehicle, front_sensor, left_front_sensor, right_front_sensor, left_sensor, right_sensor):
    if front_sensor:
        if not left_sensor:
            vehicle.move("LEFT")
        elif not right_sensor:
            vehicle.move("RIGHT")
        elif not left_front_sensor:
            vehicle.move("LEFT")
        elif not right_front_sensor:
            vehicle.move("RIGHT")
        else:
            vehicle.move("DOWN")
    else:
        vehicle.move("UP")

# 道路の描画
def draw_road(win):
    win.fill(GRAY)
    for i in range(1, 4):
        pygame.draw.line(win, WHITE, (i * LANE_WIDTH, 0), (i * LANE_WIDTH, HEIGHT), 2)

# 障害物を固定位置に生成
def create_fixed_obstacles():
    obstacles = [
        Obstacle(200, 150, 100, 50, 2, 0),
        Obstacle(400, 300, 150, 50, 0, 2),
        Obstacle(600, 100, 50, 200, -2, 0)
    ]
    return obstacles

# グラフをプロットする関数
def plot_paths(vehicle1, vehicle2):
    plt.figure(figsize=(10, 8))
    
    # 車両1の経路をプロット
    path1 = np.array(vehicle1.path)
    plt.plot(path1[:, 0], path1[:, 1], 'g', label='Vehicle 1 Path')
    
    # 車両2の経路をプロット
    path2 = np.array(vehicle2.path)
    plt.plot(path2[:, 0], path2[:, 1], 'b', label='Vehicle 2 Path')
    
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Vehicle Paths')
    plt.legend()
    plt.grid(True)
    plt.show()

# メインループ
def main():
    run = True
    clock = pygame.time.Clock()
    
    # 車両の初期位置と色
    vehicle1 = Vehicle(LANE_WIDTH * 2 - LANE_WIDTH // 2, HEIGHT - 100, GREEN)
    vehicle2 = Vehicle(LANE_WIDTH * 3 - LANE_WIDTH // 2, HEIGHT - 150, BLUE)
    
    # 障害物のリスト
    obstacles = create_fixed_obstacles()
    
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        # 車両1の自動運転
        front_sensor1, left_front_sensor1, right_front_sensor1, left_sensor1, right_sensor1 = vehicle1.detect_obstacles(obstacles)
        autonomous_drive(vehicle1, front_sensor1, left_front_sensor1, right_front_sensor1, left_sensor1, right_sensor1)
        
        # 車両2の自動運転
        front_sensor2, left_front_sensor2, right_front_sensor2, left_sensor2, right_sensor2 = vehicle2.detect_obstacles(obstacles)
        autonomous_drive(vehicle2, front_sensor2, left_front_sensor2, right_front_sensor2, left_sensor2, right_sensor2)
        
        for obstacle in obstacles:
            obstacle.move()
        
        draw_road(win)
        vehicle1.draw(win)
        vehicle2.draw(win)
        for obstacle in obstacles:
            obstacle.draw(win)
        
        pygame.display.update()
    
    pygame.quit()
    
    # 経路をプロット
    plot_paths(vehicle1, vehicle2)

if __name__ == "__main__":
    main()
