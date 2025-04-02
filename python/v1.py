import pygame
import random
import os

# 初始化 Pygame
pygame.init()

# 設定遊戲視窗的原始大小
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("大老二 Big Two")

# 設定顏色
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BUTTON_COLOR = (0, 0, 255)  # 按鈕顏色
BUTTON_HOVER_COLOR = (0, 0, 200)  # 滑鼠懸停時的按鈕顏色

# 撲克牌數據 (使用英文字花色)
suits = {"s": "黑桃", "h": "愛心", "d": "方塊", "c": "梅花"}
cards = [(suit, rank) for suit in suits.keys() for rank in range(1, 14)]  # 52 張牌

# 檢查並創建 'cards' 資料夾
if not os.path.exists("cards"):
    os.makedirs("cards")

# 玩家數據
players = [[], [], [], []]

# 初始化撲克牌並洗牌
def shuffle_deck():
    global cards, players
    random.shuffle(cards)
    for i in range(4):
        players[i] = sorted(cards[i*13:(i+1)*13], key=lambda x: (x[1], list(suits.keys()).index(x[0])))

shuffle_deck()

# 載入牌面圖片
def load_card_image(suit, rank):
    path = os.path.join("cards", f"{suit}{rank}.jpg")  # 使用 .jpg 格式
    if os.path.exists(path):
        return pygame.image.load(path)
    return None  # 如果圖片不存在

card_images = {(suit, rank): load_card_image(suit, rank) for suit in suits.keys() for rank in range(1, 14)}

current_player = 0  # 目前回合的玩家

# 切換全螢幕模式
def toggle_fullscreen():
    global screen, WIDTH, HEIGHT
    screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
    if screen.get_flags() & pygame.SCALED:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    else:
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.SCALED)

# 檢查滑鼠是否在按鈕範圍內
def is_mouse_over_button(mouse_pos, button_rect):
    return button_rect.collidepoint(mouse_pos)

# 縮放圖片
def scale_image(image, scale_factor):
    new_width = int(image.get_width() * scale_factor)
    new_height = int(image.get_height() * scale_factor)
    return pygame.transform.scale(image, (new_width, new_height))

# 遊戲主迴圈
running = True
fullscreen = False
scale_factor = 1.0  # 預設比例

# 監聽視窗大小調整
dragging = False
drag_start = None

while running:
    screen.fill(GREEN)  # 背景顏色
    
    # 顯示全螢幕按鈕
    button_rect_fullscreen = pygame.Rect(10, 10, 100, 40)  # 全螢幕按鈕位置和大小
    mouse_pos = pygame.mouse.get_pos()
    
    # 檢查滑鼠懸停，改變全螢幕按鈕顏色
    if is_mouse_over_button(mouse_pos, button_rect_fullscreen):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect_fullscreen)
        if pygame.mouse.get_pressed()[0]:  # 檢查是否點擊
            toggle_fullscreen()
            fullscreen = not fullscreen  # 切換全螢幕狀態
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect_fullscreen)
    
    # 顯示按鈕文字
    font = pygame.font.Font(None, 30)
    text = font.render("全螢幕", True, WHITE)
    screen.blit(text, (button_rect_fullscreen.x + 10, button_rect_fullscreen.y + 5))
    
    # 顯示洗牌按鈕
    button_rect_shuffle = pygame.Rect(120, 10, 100, 40)  # 洗牌按鈕位置和大小
    if is_mouse_over_button(mouse_pos, button_rect_shuffle):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect_shuffle)
        if pygame.mouse.get_pressed()[0]:  # 檢查是否點擊
            shuffle_deck()  # 洗牌
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect_shuffle)
    
    # 顯示按鈕文字
    text_shuffle = font.render("洗牌", True, WHITE)
    screen.blit(text_shuffle, (button_rect_shuffle.x + 10, button_rect_shuffle.y + 5))
    
    # 顯示玩家手牌 (用圖片)
    y_offset = 100
    for i, hand in enumerate(players):
        x_offset = 50
        for suit, rank in hand:
            card_image = card_images.get((suit, rank))
            if card_image:
                scaled_image = scale_image(card_image, scale_factor)  # 縮放圖片
                screen.blit(scaled_image, (x_offset, y_offset))
            x_offset += 50  # 調整牌間距
        y_offset += 100
    
    pygame.display.flip()
    
    # 監聽事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:  # 按上下鍵來縮放
                scale_factor *= 1.1  # 放大
            elif event.key == pygame.K_DOWN:
                scale_factor /= 1.1  # 縮小
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # 觸發視窗大小拖動
                dragging = True
                drag_start = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                dx, dy = pygame.mouse.get_pos()
                screen_width, screen_height = screen.get_size()
                new_width = max(400, screen_width + dx - drag_start[0])
                new_height = max(300, screen_height + dy - drag_start[1])
                screen = pygame.display.set_mode((new_width, new_height))
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
                drag_start = None

pygame.quit()
