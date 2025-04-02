import pygame
import random
import os
from collections import Counter

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

# 玩家數據與初始設定
players = [[], [], [], []]
current_player = 0  # 待調整：持有梅花3的玩家先出牌
selected_cards = []  # 當前玩家選中的牌
played_hand_image = None  # 顯示出的牌型圖片
last_play = None       # 上一家有效出牌的牌組（若為 None 表示沒有人出過）
pass_count = 0         # 連續過牌的人數

# Big Two 特有的牌序：
# 牌的大小順序依照: 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K, A, 2
big_two_order = {3:0, 4:1, 5:2, 6:3, 7:4, 8:5, 9:6, 10:7, 11:8, 12:9, 13:10, 1:11, 2:12}
# 花色順序：梅花 (c) < 方塊 (d) < 愛心 (h) < 黑桃 (s)
suit_order = {"c": 0, "d": 1, "h": 2, "s": 3}

# 洗牌並發牌
def shuffle_deck():
    global cards, players, current_player, last_play, pass_count
    random.shuffle(cards)
    for i in range(4):
        players[i] = sorted(cards[i * 13:(i + 1) * 13],
                            key=lambda x: (x[1], list(suits.keys()).index(x[0])))
    # 找出持有梅花3 ("c", 3) 的玩家並設為第一位
    for i in range(4):
        if ("c", 3) in players[i]:
            current_player = i
            break
    last_play = None
    pass_count = 0

shuffle_deck()

# 牌的基本尺寸與偏移量
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_SPACING = 20
CARD_Y = HEIGHT - CARD_HEIGHT + 190
CARD_OFFSET_X = 350

# 載入牌面圖片
def load_card_image(suit, rank):
    path = os.path.join("cards", f"{suit}{rank}.jpg")
    return pygame.image.load(path) if os.path.exists(path) else None

card_images = {(suit, rank): load_card_image(suit, rank)
               for suit in suits.keys() for rank in range(1, 14)}

# 載入音效（如果有）
def load_sound(filename):
    path = os.path.join("sounds", filename)
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None

valid_sound = load_sound("valid.wav")
invalid_sound = load_sound("invalid.wav")

# 牌型對應的圖片名稱（需放置在 hands 資料夾內）
hand_type_images = {
    "single": "single.png",
    "pair": "pair.png",
    "triple": "triple.png",
    "straight": "straight.png",
    "fullhouse": "fullhouse.png",
    "four_of_a_kind": "four_of_a_kind.png"
}

# 計算手牌位置，依照指定的設定
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
        start_y = (HEIGHT - total_width) // 2 + 350
        return [(WIDTH - CARD_WIDTH + 700, start_y + i * (CARD_HEIGHT // 2)) for i in range(hand_size)]
    return []

# 檢查滑鼠是否點擊到某張牌
def get_card_at_pos(pos, hand_positions):
    for i, (x, y) in enumerate(hand_positions):
        if x <= pos[0] <= x + CARD_WIDTH and y <= pos[1] <= y + CARD_HEIGHT:
            return i
    return None

# 牌型檢查
def check_hand_type(hand):
    # 單張、對子、三條
    if len(hand) == 1:
        return "single"
    elif len(hand) == 2 and hand[0][1] == hand[1][1]:
        return "pair"
    elif len(hand) == 3 and hand[0][1] == hand[1][1] == hand[2][1]:
        return "triple"
    # 五張牌：先檢查葫蘆，再檢查順子
    elif len(hand) == 5:
        ranks = [card[1] for card in hand]
        count = Counter(ranks)
        if sorted(count.values()) == [2, 3]:
            return "fullhouse"
        sorted_ranks = sorted(ranks)
        if sorted_ranks == list(range(sorted_ranks[0], sorted_ranks[0] + 5)):
            return "straight"
    return None  # 非法牌型

# 取得牌組的比較關鍵牌
def hand_key(hand, hand_type):
    if hand_type == "single":
        return max(hand, key=lambda card: (big_two_order[card[1]], suit_order[card[0]]))
    elif hand_type in ["pair", "triple"]:
        return max(hand, key=lambda card: (big_two_order[card[1]], suit_order[card[0]]))
    elif hand_type == "straight":
        return max(hand, key=lambda card: big_two_order[card[1]])
    elif hand_type == "fullhouse":
        count = Counter(card[1] for card in hand)
        triple_rank = [rank for rank, cnt in count.items() if cnt == 3][0]
        triple_cards = [card for card in hand if card[1] == triple_rank]
        return max(triple_cards, key=lambda card: suit_order[card[0]])
    elif hand_type == "four_of_a_kind":
        count = Counter(card[1] for card in hand)
        four_rank = [rank for rank, cnt in count.items() if cnt == 4][0]
        four_cards = [card for card in hand if card[1] == four_rank]
        return max(four_cards, key=lambda card: suit_order[card[0]])
    return None

# 比較兩個牌組是否 new_hand 比 last_hand 大（僅比較相同牌型）
def compare_hands(new_hand, last_hand):
    new_type = check_hand_type(new_hand)
    last_type = check_hand_type(last_hand)
    if new_type != last_type:
        return False
    new_key = hand_key(new_hand, new_type)
    last_key = hand_key(last_hand, last_type)
    if big_two_order[new_key[1]] > big_two_order[last_key[1]]:
        return True
    elif big_two_order[new_key[1]] == big_two_order[last_key[1]] and suit_order[new_key[0]] > suit_order[last_key[0]]:
        return True
    else:
        return False

# 處理玩家出牌
def play_selected_cards():
    global players, selected_cards, played_hand_image, current_player, last_play, pass_count
    if selected_cards:
        hand_type = check_hand_type(selected_cards)
        if hand_type is None:
            if invalid_sound:
                invalid_sound.play()
            return

        # 第一回合必須包含梅花3
        if last_play is None:
            if ("c", 3) not in selected_cards:
                if invalid_sound:
                    invalid_sound.play()
                return

        # 若不是第一回合，牌型必須與上一家相同且比上一家大
        if last_play is not None:
            if hand_type != check_hand_type(last_play) or not compare_hands(selected_cards, last_play):
                if invalid_sound:
                    invalid_sound.play()
                return

        # 合法出牌：更新最後出牌、播放音效、移除玩家出牌，重置過牌計數
        last_play = selected_cards.copy()
        if valid_sound:
            valid_sound.play()
        for card in selected_cards:
            if card in players[current_player]:
                players[current_player].remove(card)
        selected_cards.clear()
        pass_count = 0
        current_player = (current_player + 1) % 4

# 處理過牌（按 S）
def pass_turn():
    global current_player, pass_count, last_play
    pass_count += 1
    current_player = (current_player + 1) % 4
    # 如果連續三家過牌，則本回合結束，清除上一家的出牌
    if pass_count >= 3:
        last_play = None
        pass_count = 0

running = True
while running:
    screen.fill(GREEN)
    positions = ["bottom", "left", "top", "right"]
    # 繪製所有玩家的手牌
    for i, pos in enumerate(positions):
        card_positions = calculate_card_positions(players[i], pos)
        for j, (suit, rank) in enumerate(players[i]):
            card_image = card_images.get((suit, rank))
            if card_image:
                card_x, card_y = card_positions[j]
                # 處理選牌位移效果：根據玩家位置調整方向
                if i == current_player and (suit, rank) in selected_cards:
                    if pos == "bottom":
                        card_y -= 20
                    elif pos == "top":
                        card_y += 20
                    elif pos == "left":
                        card_x += 20  # 左邊玩家選牌向右移動
                    elif pos == "right":
                        card_x -= 20  # 右邊玩家選牌向左移動
                scaled_card = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
                screen.blit(scaled_card, (card_x, card_y))
    
    # 顯示打出的牌型圖片（若有）
    if played_hand_image:
        image_rect = played_hand_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(played_hand_image, image_rect)
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                play_selected_cards()
            elif event.key == pygame.K_s:
                pass_turn()
            elif event.key == pygame.K_r:
                shuffle_deck()
                selected_cards.clear()
                played_hand_image = None
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player_pos = positions[current_player]
                hand_positions = calculate_card_positions(players[current_player], player_pos)
                # 若為左右玩家，調整碰撞箱範圍上移20像素
                if player_pos in ["left", "right"]:
                    modified_hand_positions = [(x, y - 20) for (x, y) in hand_positions]
                else:
                    modified_hand_positions = hand_positions
                card_index = get_card_at_pos(pygame.mouse.get_pos(), modified_hand_positions)
                if card_index is not None:
                    chosen_card = players[current_player][card_index]
                    if chosen_card in selected_cards:
                        selected_cards.remove(chosen_card)
                    else:
                        selected_cards.append(chosen_card)

pygame.quit()
