import pygame
import math

# 初始化 Pygame
pygame.init()

# 設定視窗大小
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("撲克牌發牌動畫")

# 顏色
WHITE = (255, 255, 255)

# 設定 FPS
clock = pygame.time.Clock()
FPS = 60

# 牌的起始位置（中央）
start_x, start_y = WIDTH // 2, HEIGHT // 2

# 玩家座標 (四個角落)
player_positions = [
    (150, 100),  # 玩家1（左上）
    (650, 100),  # 玩家2（右上）
    (650, 500),  # 玩家3（右下）
    (150, 500)   # 玩家4（左下）
]

# 載入牌的圖片（請更換為你自己的撲克牌圖片）
card_image = pygame.Surface((60, 90), pygame.SRCALPHA)  # 產生透明背景的矩形
pygame.draw.rect(card_image, (255, 0, 0), (0, 0, 60, 90), border_radius=10)  # 繪製紅色卡片

class Card:
    def __init__(self, target_pos):
        self.x, self.y = start_x, start_y
        self.target_x, self.target_y = target_pos
        self.angle = 0  # 旋轉角度
        self.speed = 10  # 移動速度
        self.rotation_speed = 5  # 旋轉速度
        self.moving = True

    def update(self):
        if self.moving:
            # 計算移動向量
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.hypot(dx, dy)
            
            if distance < self.speed:
                self.x, self.y = self.target_x, self.target_y
                self.moving = False  # 停止移動
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                self.angle += self.rotation_speed  # 旋轉動畫
                self.angle %= 360  # 確保角度不超過 360 度
    
    def draw(self, surface):
        rotated_card = pygame.transform.rotate(card_image, self.angle)
        rect = rotated_card.get_rect(center=(self.x, self.y))
        surface.blit(rotated_card, rect.topleft)

# 創建四張卡片
cards = [Card(pos) for pos in player_positions]

# 遊戲主迴圈
running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 更新與繪製卡片
    for card in cards:
        card.update()
        card.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
