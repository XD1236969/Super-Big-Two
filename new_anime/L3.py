import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

def draw_cylinder_2d(x, y, width, height):
    """用 2D 方法模擬 3D 圓柱"""
    pygame.draw.ellipse(screen, GRAY, (x, y, width, height // 4))  # 頂部橢圓
    pygame.draw.rect(screen, GRAY, (x, y + height // 8, width, height // 2))  # 圓柱體
    pygame.draw.ellipse(screen, WHITE, (x, y + height // 2, width, height // 4))  # 底部橢圓

running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_cylinder_2d(300, 200, 100, 200)  # 在畫面上繪製 2D 圓柱

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
