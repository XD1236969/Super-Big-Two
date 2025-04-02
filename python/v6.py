import pygame
import random
import os

# 初始化 Pygame
pygame.init()

# 設定遊戲視窗大小
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("大老二 Big Two")

# 設定顏色
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)

# 撲克牌數據
suits = {"s": "黑桃", "h": "愛心", "d": "方塊", "c": "梅花"}
cards = [(suit, rank) for suit in suits.keys() for rank in range(1, 14)]  # 52 張牌

# 確保資料夾存在
os.makedirs("cards", exist_ok=True)
os.makedirs("hands", exist_ok=True)
os.makedirs("sounds", exist_ok=True)

# 玩家數據
players = [[], [], [], []]

# 洗牌並發牌
def shuffle_deck():
    global cards, players
    random.shuffle(cards)
    for i in range(4):
        players[i] = sorted(cards[i * 13:(i + 1) * 13], key=lambda x: (x[1], list(suits.keys()).index(x[0])))

shuffle_deck()

# 牌的基本尺寸與偏移量
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_SPACING = 20
CARD_Y = HEIGHT - CARD_HEIGHT + 190
CARD_OFFSET_X = 350

def load_card_image(suit, rank):
    path = os.path.join("cards", f"{suit}{rank}.jpg")
    return pygame.image.load(path) if os.path.exists(path) else None

card_images = {(suit, rank): load_card_image(suit, rank) for suit in suits.keys() for rank in range(1, 14)}

def calculate_card_positions(hand, position):
    hand_size = len(hand)
    total_width = hand_size * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING
    
    if position == "bottom":
        start_x = (WIDTH - total_width) // 2 + CARD_OFFSET_X
        return [(start_x + i * (CARD_WIDTH + CARD_SPACING), CARD_Y) for i in range(hand_size)]
    elif position == "top":
        start_x = (WIDTH - total_width) // 2 + 350
        return [(start_x + i * (CARD_WIDTH + CARD_SPACING), 20) for i in range(hand_size)]
    elif position == "left":
        start_y = (HEIGHT - total_width) // 2 + 350
        return [(20, start_y + i * (CARD_HEIGHT // 2)) for i in range(hand_size)]
    elif position == "right":
        start_y = (HEIGHT - total_width) // 2 +350
        return [(WIDTH - CARD_WIDTH + 700, start_y + i * (CARD_HEIGHT // 2)) for i in range(hand_size)]
    return []

running = True
while running:
    screen.fill(GREEN)
    
    # 繪製玩家手牌
    positions = ["bottom", "left", "top", "right"]
    for i, position in enumerate(positions):
        card_positions = calculate_card_positions(players[i], position)
        for j, (suit, rank) in enumerate(players[i]):
            card_image = card_images.get((suit, rank))
            if card_image:
                card_x, card_y = card_positions[j]
                scaled_card = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
                screen.blit(scaled_card, (card_x, card_y))
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
