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
BUTTON_COLOR = (0, 0, 255)
BUTTON_HOVER_COLOR = (0, 0, 200)

# 撲克牌數據
suits = {"s": "黑桃", "h": "愛心", "d": "方塊", "c": "梅花"}
cards = [(suit, rank) for suit in suits.keys() for rank in range(1, 14)]  # 52 張牌

# 檢查並創建 'cards' 資料夾
if not os.path.exists("cards"):
    os.makedirs("cards")

# 玩家數據
players = [[], [], [], []]

# 洗牌並發牌
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

current_player = 0  # 當前玩家
selected_cards = []  # 存放選中的牌

# 牌的基本尺寸
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_SPACING = 20
CARD_Y = HEIGHT - CARD_HEIGHT - 20  # 牌的位置

# 讓牌有些間距並不超過螢幕
def calculate_card_positions(hand):
    hand_size = len(hand)
    total_width = hand_size * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING
    start_x = (WIDTH - total_width) // 2
    positions = [(start_x + i * (CARD_WIDTH + CARD_SPACING), CARD_Y) for i in range(hand_size)]
    return positions

# 檢查滑鼠是否點擊到某張牌
def get_card_at_pos(pos, hand_positions):
    for i, (x, y) in enumerate(hand_positions):
        if x <= pos[0] <= x + CARD_WIDTH and y <= pos[1] <= y + CARD_HEIGHT:
            return i
    return None

# 處理玩家出牌
def play_selected_cards():
    global players, selected_cards
    if selected_cards:
        # 直接移除選中的牌
        for card in selected_cards:
            if card in players[current_player]:
                players[current_player].remove(card)
        selected_cards.clear()

# 遊戲主迴圈
running = True
while running:
    screen.fill(GREEN)  # 設定背景顏色
    hand = players[current_player]
    card_positions = calculate_card_positions(hand)

    # 繪製手牌
    for i, (suit, rank) in enumerate(hand):
        card_image = card_images.get((suit, rank))
        if card_image:
            card_x, card_y = card_positions[i]
            if (suit, rank) in selected_cards:
                card_y -= 20  # 被選中的牌會上移
            scaled_card = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
            screen.blit(scaled_card, (card_x, card_y))

    # 更新畫面
    pygame.display.flip()

    # 事件監聽
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # 按 Enter 出牌
                play_selected_cards()
            elif event.key == pygame.K_r:  # 按 R 重新洗牌
                shuffle_deck()
                selected_cards.clear()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵點擊選擇牌
                card_index = get_card_at_pos(pygame.mouse.get_pos(), card_positions)
                if card_index is not None:
                    chosen_card = hand[card_index]
                    if chosen_card in selected_cards:
                        selected_cards.remove(chosen_card)  # 取消選擇
                    else:
                        selected_cards.append(chosen_card)  # 選擇新牌
