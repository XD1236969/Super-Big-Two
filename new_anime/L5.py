import pygame
import random, math

# 初始化 pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Link Start - 2D 模擬 3D")
clock = pygame.time.Clock()

# 顏色定義
BLACK = (0, 0, 0)

# 2D 模擬 3D 圓柱類別
class Cylinder2D:
    def __init__(self, angle, color):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = angle
        self.color = color
        self.speed = 5
        self.length = 50  # 長條長度
        self.width = 10   # 長條寬度

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
    
    def draw(self, screen):
        # 計算圓柱的端點，用線條模擬立體感
        end_x = self.x + self.length * math.cos(self.angle)
        end_y = self.y + self.length * math.sin(self.angle)
        # 模擬陰影與光澤效果，先畫較深的部分，再疊上較亮的部分
        darker_color = (max(self.color[0]-50,0), max(self.color[1]-50,0), max(self.color[2]-50,0))
        pygame.draw.line(screen, darker_color, (self.x, self.y), (end_x, end_y), self.width)
        # 可加上漸層或橢圓來增強立體效果 (此處簡單示範)

def emit_cylinders_2d():
    """從中心發射多個 2D 圓柱物件，方向均勻分布"""
    num = 20
    for i in range(num):
        angle = 2 * math.pi * i / num
        color = (random.randint(100,255), random.randint(100,255), random.randint(100,255))
        cylinders.append(Cylinder2D(angle, color))

# 儲存 2D 圓柱物件
cylinders = []

running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            emit_cylinders_2d()
    
    for cyl in cylinders:
        cyl.move()
        cyl.draw(screen)
    
    # 移除超出畫面範圍的圓柱物件
    cylinders = [cyl for cyl in cylinders if 0 <= cyl.x <= WIDTH and 0 <= cyl.y <= HEIGHT]
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
