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

# ---------------------------
# 大老二完整規則說明：
#
# 1. 發牌與起手：
#    - 使用 52 張牌，四位玩家各 13 張。
#    - 持有梅花3的玩家必須先出牌，且第一手牌必須包含梅花3。
#
# 2. 牌型：
#    - 單張、對子、三條。
#    - 5 張牌型包含：順子、葫蘆、鐵支（四條炸彈）、桐花順（同花順）。
#
# 3. 出牌規則：
#    - 第一手出牌必須包含梅花3。
#    - 後續出牌必須與上一家牌型相同且比上一家牌大，但 bomb（鐵支或桐花順）可強壓其他牌型。
#    - 若玩家無法或不願出牌，可按 S 過牌；當其他三家都過牌時，重置出牌限制，
#      回合權交回最後成功出牌的玩家，此時可自由出新牌型。
#
# 4. 勝利條件：第一位出完手牌的玩家獲勝。
# ---------------------------

# 玩家資料與初始設定
players = [[], [], [], []]
current_player = 0      # 持有梅花3的玩家先出牌
selected_cards = []     # 當前玩家選中的牌
played_hand_image = None  # 顯示出的牌型圖片
last_play = None        # 上一家有效出牌的牌組 (None 表示無出牌)
winner = None           # 遊戲勝利者
last_valid_player = None  # 紀錄最後成功出牌的玩家
passed_players = []       # 紀錄本輪跳過的玩家

# Big Two 牌序與花色順序
big_two_order = {3:0, 4:1, 5:2, 6:3, 7:4, 8:5, 9:6, 10:7, 11:8, 12:9, 13:10, 1:11, 2:12}
suit_order = {"c":0, "d":1, "h":2, "s":3}

# 洗牌發牌，並找出持有梅花3的玩家
def shuffle_deck():
    global cards, players, current_player, last_play, winner, last_valid_player, passed_players, played_hand_image
    random.shuffle(cards)
    for i in range(4):
        players[i] = sorted(cards[i * 13:(i + 1) * 13],
                            key=lambda x: (x[1], list(suits.keys()).index(x[0])))
    for i in range(4):
        if ("c", 3) in players[i]:
            current_player = i
            break
    last_play = None
    winner = None
    played_hand_image = None
    last_valid_player = None
    passed_players = []

shuffle_deck()

# 基本牌尺寸與偏移
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

# 載入音效與圖片
def load_sound(filename):
    path = os.path.join("sounds", filename)
    return pygame.mixer.Sound(path) if os.path.exists(path) else None

valid_sound = load_sound("valid.wav")
invalid_sound = load_sound("invalid.wav")
skip_sound = load_sound("skip.wav")

# 載入手牌出牌與跳過圖片（放在 hands 資料夾）
hand_type_images = {
    "single": "single.png",
    "pair": "pair.png",
    "triple": "triple.png",
    "straight": "straight.png",
    "fullhouse": "fullhouse.png",
    "four_of_a_kind": "four_of_a_kind.png",
    "straight_flush": "straight_flush.png"
}
hand_type_images_scaled = {}
for hand_type, file_name in hand_type_images.items():
    image_path = os.path.join("hands", file_name)
    if os.path.exists(image_path):
        image = pygame.image.load(image_path)
        fixed_width = 100
        fixed_height = 75
        hand_type_images_scaled[hand_type] = pygame.transform.smoothscale(image, (fixed_width, fixed_height))
    else:
        hand_type_images_scaled[hand_type] = None

# 計算手牌位置
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

# 判斷滑鼠點擊牌的範圍
def get_card_at_pos(pos, hand_positions):
    for i, (x, y) in enumerate(hand_positions):
        if x <= pos[0] <= x + CARD_WIDTH and y <= pos[1] <= y + CARD_HEIGHT:
            return i
    return None

# 牌型判斷：新增鐵支與桐花順
def check_hand_type(hand):
    if len(hand) == 1:
        return "single"
    elif len(hand) == 2 and hand[0][1] == hand[1][1]:
        return "pair"
    elif len(hand) == 3 and hand[0][1] == hand[1][1] == hand[2][1]:
        return "triple"
    elif len(hand) == 5:
        ranks = [card[1] for card in hand]
        count = Counter(ranks)
        suits_in_hand = [card[0] for card in hand]
        # 先檢查桐花順：同花且連續
        if len(set(suits_in_hand)) == 1:
            sorted_ranks = sorted(ranks)
            if sorted_ranks == list(range(sorted_ranks[0], sorted_ranks[0] + 5)):
                return "straight_flush"
        # 檢查鐵支：四張相同點數
        if 4 in count.values():
            return "four_of_a_kind"
        # 檢查葫蘆：3+2 組合
        if sorted(count.values()) == [2, 3]:
            return "fullhouse"
        # 檢查順子：連續五張
        sorted_ranks = sorted(ranks)
        if sorted_ranks == list(range(sorted_ranks[0], sorted_ranks[0] + 5)):
            return "straight"
    return None

# 取得關鍵牌（決定牌組大小）
def hand_key(hand, hand_type):
    if hand_type == "single":
        return max(hand, key=lambda card: (big_two_order[card[1]], suit_order[card[0]]))
    elif hand_type in ["pair", "triple"]:
        return max(hand, key=lambda card: (big_two_order[card[1]], suit_order[card[0]]))
    elif hand_type in ["straight", "straight_flush"]:
        return max(hand, key=lambda card: (big_two_order[card[1]], suit_order[card[0]]))
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

# 比較牌組大小，包含 bomb 強壓功能
def compare_hands(new_hand, last_hand):
    new_type = check_hand_type(new_hand)
    last_type = check_hand_type(last_hand)
    bomb_types = {"four_of_a_kind", "straight_flush"}
    if new_type in bomb_types and last_type not in bomb_types:
        return True
    if new_type not in bomb_types and last_type in bomb_types:
        return False
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

# 處理玩家出牌：成功出牌後清空 passed_players
def play_selected_cards():
    global players, selected_cards, played_hand_image, current_player, last_play, winner, last_valid_player, passed_players
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

        # 非第一回合必須與上一家牌型相同且比其大，除非 bomb 強壓
        if last_play is not None:
            if hand_type != check_hand_type(last_play) and hand_type not in {"four_of_a_kind", "straight_flush"}:
                if invalid_sound:
                    invalid_sound.play()
                return
            if not compare_hands(selected_cards, last_play):
                if invalid_sound:
                    invalid_sound.play()
                return

        # 合法出牌：更新 last_play 並記錄最後成功出牌的玩家
        last_play = selected_cards.copy()
        last_valid_player = current_player
        if valid_sound:
            valid_sound.play()
        if hand_type in hand_type_images:
            image_path = os.path.join("hands", hand_type_images[hand_type])
            if os.path.exists(image_path):
                played_hand_image = pygame.image.load(image_path)
                orig_rect = played_hand_image.get_rect()
                new_size = (int(orig_rect.width * 0.7), int(orig_rect.height * 0.7))
                played_hand_image = pygame.transform.smoothscale(played_hand_image, new_size)
            else:
                played_hand_image = None
        else:
            played_hand_image = None

        # 移除出牌玩家手牌，清空選牌與跳過列表
        for card in selected_cards:
            if card in players[current_player]:
                players[current_player].remove(card)
        selected_cards.clear()
        passed_players = []  # 重置本輪跳過玩家

        # 檢查是否有人出完牌
        if len(players[current_player]) == 0:
            winner = current_player
        else:
            current_player = (current_player + 1) % 4

# 載入跳過圖片（若存在）
skip_image_path = os.path.join("hands", "skip.png")
skip_image = pygame.image.load(skip_image_path) if os.path.exists(skip_image_path) else None

# 處理過牌，利用 passed_players 記錄本輪跳過玩家
def pass_turn():
    global current_player, passed_players, last_play, played_hand_image
    if current_player not in passed_players:
        passed_players.append(current_player)
    if skip_sound:
        skip_sound.play()
    if skip_image:
        played_hand_image = skip_image
    # 若其他三家皆跳過，則重置出牌限制，回合權交回最後成功出牌的玩家
    if len(passed_players) == 3:
        last_play = None
        passed_players = []
        if last_valid_player is not None:
            current_player = last_valid_player
    else:
        current_player = (current_player + 1) % 4

# 遊戲主迴圈
running = True
while running:
    screen.fill(GREEN)
    positions = ["bottom", "left", "top", "right"]

    for i, pos in enumerate(positions):
        card_positions = calculate_card_positions(players[i], pos)
        for j, (suit, rank) in enumerate(players[i]):
            card_image = card_images.get((suit, rank))
            if card_image:
                card_x, card_y = card_positions[j]
                if i == current_player and (suit, rank) in selected_cards:
                    if pos == "bottom":
                        card_y -= 20
                    elif pos == "top":
                        card_y += 20
                    elif pos == "left":
                        card_x += 20
                    elif pos == "right":
                        card_x -= 20
                scaled_card = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
                screen.blit(scaled_card, (card_x, card_y))
    
    if played_hand_image:
        image_rect = played_hand_image.get_rect(center=(WIDTH // 2 + 400, HEIGHT // 2 + 100))
        screen.blit(played_hand_image, image_rect)

    if winner is not None:
        font = pygame.font.SysFont(None, 72)
        win_text = f"Player {winner+1} Wins!"
        text_surf = font.render(win_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text_surf, text_rect)
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if winner is not None:
                if event.key == pygame.K_r:
                    shuffle_deck()
                    selected_cards.clear()
                    played_hand_image = None
                    winner = None
            else:
                if event.key == pygame.K_RETURN:
                    play_selected_cards()
                elif event.key == pygame.K_s:
                    pass_turn()
                elif event.key == pygame.K_r:
                    shuffle_deck()
                    selected_cards.clear()
                    played_hand_image = None

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and winner is None:
                player_pos = positions[current_player]
                hand_positions = calculate_card_positions(players[current_player], player_pos)
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
