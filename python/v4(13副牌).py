import pygame
import random
import os
from collections import Counter

# 初始化 Pygame
pygame.init()

# 設定遊戲視窗大小
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("大老二 Big Two - 13 副牌")

# 設定顏色
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)

# 撲克牌數據（13 副牌）
suits = {"s": "黑桃", "h": "愛心", "d": "方塊", "c": "梅花"}
cards = [(suit, rank) for suit in suits.keys() for rank in range(1, 14)] * 13  # 13 副牌

# 確保資料夾存在
os.makedirs("cards", exist_ok=True)
os.makedirs("hands", exist_ok=True)
os.makedirs("sounds", exist_ok=True)

# 載入牌面圖片
def load_card_image(suit, rank):
    path = os.path.join("cards", f"{suit}{rank}.jpg")
    return pygame.image.load(path) if os.path.exists(path) else None

card_images = {(suit, rank): load_card_image(suit, rank) for suit in suits.keys() for rank in range(1, 14)}

# 玩家數據（4 人，每人 169 張牌）
players = [[] for _ in range(4)]
selected_cards = []
played_hand = []

# 洗牌並發牌
def shuffle_deck():
    global cards, players, selected_cards, played_hand
    random.shuffle(cards)
    for i in range(4):
        players[i] = sorted(cards[i * 169:(i + 1) * 169], key=lambda x: (x[1], list(suits.keys()).index(x[0])))
    selected_cards.clear()
    played_hand.clear()

shuffle_deck()

# 牌的基本尺寸與偏移量（放大 1.5 倍）
CARD_WIDTH = int(50 * 1.5)
CARD_HEIGHT = int(75 * 1.5)
CARD_SPACING = 10
ROW_LIMIT = 13  # 每行最多 13 張牌
SCROLL_Y = -1000  # 初始上移 1000 像素

# 計算牌的位置
def calculate_card_positions(hand):
    positions = []
    for i, card in enumerate(hand):
        row = i // ROW_LIMIT
        col = i % ROW_LIMIT
        x = 50 + col * (CARD_WIDTH + CARD_SPACING)
        y = HEIGHT - 200 + row * (CARD_HEIGHT + CARD_SPACING) + SCROLL_Y  # 13 張換行，上移 1000 像素
        positions.append((x, y))
    return positions

# 判斷牌型
def check_hand_type(hand):
    if len(hand) == 1:
        return "single"
    elif len(hand) == 2 and hand[0][1] == hand[1][1]:
        return "pair"
    elif len(hand) == 3 and hand[0][1] == hand[1][1] == hand[2][1]:
        return "triple"
    elif len(hand) == 5:
        ranks = sorted([card[1] for card in hand])
        suits = [card[0] for card in hand]
        rank_counts = Counter(ranks)
        is_flush = len(set(suits)) == 1
        is_straight = ranks == list(range(ranks[0], ranks[0] + 5))
        if is_flush and is_straight:
            return "straight_flush"
        elif 4 in rank_counts.values():
            return "four_of_a_kind"
        elif 3 in rank_counts.values() and 2 in rank_counts.values():
            return "full_house"
        elif is_flush:
            return "flush"
        elif is_straight:
            return "straight"
    return None

# 出牌
def play_selected_cards():
    global selected_cards, played_hand
    if selected_cards:
        hand_type = check_hand_type(selected_cards)
        if hand_type:
            played_hand = selected_cards[:]
            for card in selected_cards:
                players[current_player].remove(card)
            selected_cards.clear()

# 遊戲主迴圈
running = True
current_player = 0
while running:
    screen.fill(GREEN)
    hand = players[current_player]
    card_positions = calculate_card_positions(hand)

    # 繪製玩家手牌
    for i, (suit, rank) in enumerate(hand):
        card_x, card_y = card_positions[i]
        card_image = card_images.get((suit, rank))
        if card_image:
            scaled_card = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
            screen.blit(scaled_card, (card_x, card_y))
        else:
            pygame.draw.rect(screen, WHITE, (card_x, card_y, CARD_WIDTH, CARD_HEIGHT))  # 簡單用白色方塊代替卡牌
            font = pygame.font.Font(None, 20)
            text = font.render(f"{suit}{rank}", True, (0, 0, 0))
            screen.blit(text, (card_x + 5, card_y + 5))
    
    # 繪製打出的牌
    for i, (suit, rank) in enumerate(played_hand):
        x = WIDTH // 2 + i * (CARD_WIDTH + CARD_SPACING) - (len(played_hand) * (CARD_WIDTH + CARD_SPACING)) // 2
        y = HEIGHT // 2 - 100
        card_image = card_images.get((suit, rank))
        if card_image:
            scaled_card = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
            screen.blit(scaled_card, (x, y))

    pygame.display.flip()

    # 事件監聽
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # 按 R 重新洗牌
                shuffle_deck()
            elif event.key == pygame.K_UP:
                SCROLL_Y += 50  # 向上滾動
            elif event.key == pygame.K_DOWN:
                SCROLL_Y -= 50  # 向下滾動
            elif event.key == pygame.K_RETURN:  # 按 Enter 出牌
                play_selected_cards()
pygame.quit()
