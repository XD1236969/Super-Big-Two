import pygame
import random
import math

# 初始化 pygame
pygame.init()

# 視窗設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Link Start 動畫")
clock = pygame.time.Clock()

# 顏色定義
BLACK = (0, 0, 0)

# 圓柱（長條形）類別
class Cylinder:
    def __init__(self, x, y, angle, color):
        self.x = x
        self.y = y
        self.speed = 5
        self.angle = angle
        self.color = color
        self.length = 20
        self.width = 5
    
    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
    
    def draw(self, screen):
        end_x = self.x + self.length * math.cos(self.angle)
        end_y = self.y + self.length * math.sin(self.angle)
        pygame.draw.line(screen, self.color, (self.x, self.y), (end_x, end_y), self.width)

# 圓柱列表
cylinders = []

def emit_cylinders():
    """從中心發射多個圓柱，方向均勻分布。"""
    num = 20  # 發射數量
    for i in range(num):
        angle = 2 * math.pi * i / num
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        cylinders.append(Cylinder(WIDTH // 2, HEIGHT // 2, angle, color))

# 遊戲主迴圈
running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            emit_cylinders()
    
    # 更新與繪製所有圓柱
    for cyl in cylinders:
        cyl.move()
        cyl.draw(screen)
    
    # 移除超出畫面的圓柱
    cylinders = [cyl for cyl in cylinders if 0 <= cyl.x <= WIDTH and 0 <= cyl.y <= HEIGHT]
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()