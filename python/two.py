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

# 載入牌面圖片
def load_card_image(suit, rank):
    path = os.path.join("cards", f"{suit}{rank}.jpg")
    return pygame.image.load(path) if os.path.exists(path) else None

card_images = {(suit, rank): load_card_image(suit, rank) for suit in suits.keys() for rank in range(1, 14)}

# 載入音效（如果有）
def load_sound(file):
    path = os.path.join("sounds", file)
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None

valid_sound = load_sound("valid.wav")
invalid_sound = load_sound("invalid.wav")

current_player = 0  # 當前玩家
selected_cards = []  # 存放選中的牌
played_hand_image = None  # 打出的牌型圖片

# 牌的基本尺寸與偏移量
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_SPACING = 20
CARD_Y = HEIGHT - CARD_HEIGHT - 20
CARD_OFFSET_X = 300  # 向右偏移 50px

# 讓牌有些間距並不超過螢幕
def calculate_card_positions(hand):
    hand_size = len(hand)
    total_width = hand_size * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING
    start_x = (WIDTH - total_width) // 2 + CARD_OFFSET_X
    return [(start_x + i * (CARD_WIDTH + CARD_SPACING), CARD_Y) for i in range(hand_size)]

# 檢查滑鼠是否點擊到某張牌
def get_card_at_pos(pos, hand_positions):
    for i, (x, y) in enumerate(hand_positions):
        if x <= pos[0] <= x + CARD_WIDTH and y <= pos[1] <= y + CARD_HEIGHT:
            return i
    return None

# 牌型對應的圖片名稱
hand_type_images = {
    "single": "single.jpg",
    "pair": "pair.jpg",
    "triple": "triple.jpg",
    "straight": "straight.jpg",
    "fullhouse": "fullhouse.jpg",
    "four_of_a_kind": "four_of_a_kind.jpg"
}


from collections import Counter

from collections import Counter


from collections import Counter

def check_hand_type(hand):
    if len(hand) == 1:
        return "single"
    elif len(hand) == 2 and hand[0][1] == hand[1][1]:
        return "pair"
    elif len(hand) == 3 and hand[0][1] == hand[1][1] == hand[2][1]:
        return "triple"
    elif len(hand) == 5:
        suits = [card[0] for card in hand]  # 取花色
        ranks = [card[1] for card in hand]  # 取數字
        rank_counts = Counter(ranks)  # 計算每個點數的數量

        print(f"手牌: {hand}")  # Debug: 印出手牌
        print(f"點數計數: {rank_counts}")  # Debug: 印出點數計數

        is_flush = len(set(suits)) == 1  # 是否同花
        sorted_ranks = sorted(ranks)
        is_straight = sorted_ranks == list(range(sorted_ranks[0], sorted_ranks[0] + 5))  # 是否順子
        
        if set(ranks) == {1, 10, 11, 12, 13} and is_flush:  # 皇家同花順
            return "royal_flush"
        elif is_flush and is_straight:  # 同花順
            return "straight_flush"
        elif 4 in rank_counts.values():  # 四條
            return "four_of_a_kind"
        elif 3 in rank_counts.values() and 2 in rank_counts.values():  # 確保是 3 張 + 2 張
            return "full_house"
        elif is_flush:  # 同花
            return "flush"
        elif is_straight:  # 順子
            return "straight"

    return None  # 不合法牌型




# 處理玩家出牌
def play_selected_cards():
    global players, selected_cards, played_hand_image
    if selected_cards:
        hand_type = check_hand_type(selected_cards)  # 檢查牌型

        if hand_type in hand_type_images:
            image_path = os.path.join("hands", hand_type_images[hand_type])
            if os.path.exists(image_path):
                played_hand_image = pygame.image.load(image_path)  # 顯示牌型圖片
            else:
                played_hand_image = None

            if valid_sound:
                valid_sound.play()  # 撥放成功音效

            # 移除選中的牌
            for card in selected_cards:
                if card in players[current_player]:
                    players[current_player].remove(card)
            selected_cards.clear()
        else:
            if invalid_sound:
                invalid_sound.play()  # 撥放錯誤音效

# 遊戲主迴圈
running = True
while running:
    screen.fill(GREEN)
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

    # 繪製打出的牌型圖片（如果有）
    if played_hand_image:
        image_rect = played_hand_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(played_hand_image, image_rect)

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
                played_hand_image = None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵點擊選擇牌
                card_index = get_card_at_pos(pygame.mouse.get_pos(), card_positions)
                if card_index is not None:
                    chosen_card = hand[card_index]
                    selected_cards.remove(chosen_card) if chosen_card in selected_cards else selected_cards.append(chosen_card)

pygame.quit()
