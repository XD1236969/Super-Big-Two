import pygame
import random
from particle_effects import ParticleEffectManager

# 初始化 Pygame
pygame.init()

# 初始畫面設定
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Particle Shower")

# 時鐘設定
clock = pygame.time.Clock()
particle_manager = ParticleEffectManager()

# 自動模式旗標與 Timer 事件
auto_mode = False
AUTO_EVENT = pygame.USEREVENT + 1  # 自定義事件 ID

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 當視窗大小改變時更新尺寸變數
        if event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.size
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

        # 按下左鍵觸發粒子效果（手動模式）
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                particle_manager.trigger_effect(mouse_pos, color=None, duration=1500, particle_count=150)

        # 按下 A 鍵切換自動模式
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                auto_mode = not auto_mode
                if auto_mode:
                    # 開啟自動模式，每 100 毫秒觸發一次事件
                    pygame.time.set_timer(AUTO_EVENT, 10)
                else:
                    # 關閉自動模式
                    pygame.time.set_timer(AUTO_EVENT, 0)

        # 自動模式觸發事件：隨機位置產生粒子效果
        if event.type == AUTO_EVENT and auto_mode:
            random_pos = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            particle_manager.trigger_effect(random_pos, color=None, duration=1500, particle_count=150)

    # 更新特效
    particle_manager.update()

    # 繪製畫面
    screen.fill((0, 0, 0))
    particle_manager.draw(screen)
    pygame.display.flip()

    # 每秒最大幀數
    clock.tick(60)

pygame.quit()
