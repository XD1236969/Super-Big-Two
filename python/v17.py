import pygame
import random
import os
import math
from collections import Counter

# 初始化 Pygame 與 Mixer
pygame.init()
pygame.mixer.init()

# 設定遊戲視窗大小
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("大老二 Big Two")

# 設定顏色
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
GRAY = (180, 180, 180)
DARKGRAY = (100, 100, 100)
BLACK = (0, 0, 0)

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
# (此處略……)
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

# 預設音效
valid_sound = load_sound("valid.wav")
invalid_sound = load_sound("invalid.wav")
skip_sound = load_sound("skip.wav")
deal_sound = load_sound("deal.wav")      # 發牌音效
select_sound = load_sound("select.wav")  # 選牌音效

# 各牌型專屬音效（包含一條龍與桐花一條龍）
hand_type_sounds = {
    "single": load_sound("single.wav"),
    "pair": load_sound("pair.wav"),
    "triple": load_sound("triple.wav"),
    "straight": load_sound("straight.wav"),
    "fullhouse": load_sound("fullhouse.wav"),
    "four_of_a_kind": load_sound("four_of_a_kind.wav"),
    "straight_flush": load_sound("straight_flush.wav"),
    "dragon": load_sound("dragon.wav"),           # 一條龍
    "flush_dragon": load_sound("flush_dragon.wav")  # 桐花一條龍
}

# 載入手牌出牌與跳過圖片（放在 hands 資料夾）
hand_type_images = {
    "single": "single.png",
    "pair": "pair.png",
    "triple": "triple.png",
    "straight": "straight.png",
    "fullhouse": "fullhouse.png",
    "four_of_a_kind": "four_of_a_kind.png",
    "straight_flush": "straight_flush.png",
    "dragon": "dragon.png",           # 可自行放置一條龍圖片
    "flush_dragon": "flush_dragon.png"  # 可自行放置桐花一條龍圖片
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

# 牌型判斷：新增一條龍與桐花一條龍（13 張牌）
def check_hand_type(hand):
    # 檢查一條龍 / 桐花一條龍：13 張牌必須包含所有牌點，依大老二順序為 [3,4,5,...,13,1,2]
    if len(hand) == 13:
        sorted_cards = sorted(hand, key=lambda card: big_two_order[card[1]])
        expected = [3,4,5,6,7,8,9,10,11,12,13,1,2]
        if [card[1] for card in sorted_cards] == expected:
            if len(set(card[0] for card in hand)) == 1:
                return "flush_dragon"  # 桐花一條龍
            else:
                return "dragon"        # 一條龍

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
        # 檢查桐花順：同花且連續
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
    bomb_types = {"four_of_a_kind", "straight_flush", "dragon", "flush_dragon"}
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

# --------------------
# 發牌動畫相關變數與類別
dealing_animation = False   # 是否處於發牌動畫狀態
animated_cards = []         # 正在動畫中的卡片物件
deal_order = []             # (player_index, card) 的發牌順序
next_deal_time = 0          # 下一張牌加入動畫的時間（以 pygame.time.get_ticks() 計算）

def get_deal_target(player_index):
    positions_names = ["bottom", "left", "top", "right"]
    pos_name = positions_names[player_index]
    hand_count = len(players[player_index])
    # 模擬該玩家手牌增加一張，用 dummy list 計算位置
    dummy_hand = [None] * (hand_count + 1)
    card_positions = calculate_card_positions(dummy_hand, pos_name)
    return card_positions[-1]

class AnimatedCard:
    def __init__(self, card, target_pos, player_index):
        self.card = card
        self.player_index = player_index
        self.x, self.y = WIDTH // 2, HEIGHT // 2  # 起始位置：螢幕中央
        self.target_x, self.target_y = target_pos
        self.angle = 0
        self.speed = 15            # 調整移動速度
        self.rotation_speed = 5    # 調整旋轉速度
        self.moving = True

    def update(self):
        if self.moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.hypot(dx, dy)
            if distance < self.speed:
                self.x, self.y = self.target_x, self.target_y
                self.moving = False
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                self.angle = (self.angle + self.rotation_speed) % 360

    def draw(self, surface):
        card_img = card_images.get(self.card)
        if card_img:
            scaled = pygame.transform.scale(card_img, (CARD_WIDTH, CARD_HEIGHT))
        else:
            scaled = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            scaled.fill(WHITE)
        rotated = pygame.transform.rotate(scaled, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect.topleft)

def finalize_dealing():
    global players, current_player
    # 發牌完成後，將各玩家手牌排序，並找出持有梅花3的玩家
    for i in range(4):
        players[i] = sorted(players[i], key=lambda x: (x[1], list(suits.keys()).index(x[0])))
        if ("c", 3) in players[i]:
            current_player = i

def start_dealing():
    global cards, players, dealing_animation, animated_cards, deal_order, next_deal_time
    global last_play, winner, played_hand_image, last_valid_player, passed_players
    random.shuffle(cards)
    # 清空玩家手牌
    players = [ [] for _ in range(4) ]
    dealing_animation = True
    animated_cards = []
    deal_order = []
    # 建立發牌順序：依序發 13 輪，每輪 4 張牌（玩家順序：0,1,2,3）
    card_index = 0
    for r in range(13):
        for p in range(4):
            deal_order.append( (p, cards[card_index]) )
            card_index += 1
    next_deal_time = pygame.time.get_ticks() + 100  # 每 100 毫秒發一張牌
    last_play = None
    winner = None
    played_hand_image = None
    last_valid_player = None
    passed_players = []

# 特殊發牌：指定四家都獲得同花一條龍
def special_deal_flush_dragon():
    global players, current_player, last_play, winner, played_hand_image, last_valid_player, passed_players
    order = [3,4,5,6,7,8,9,10,11,12,13,1,2]
    # 分別以四種花色給每家發同花一條龍
    players[0] = [("s", rank) for rank in order]
    players[1] = [("h", rank) for rank in order]
    players[2] = [("d", rank) for rank in order]
    players[3] = [("c", rank) for rank in order]
    for i in range(4):
        if ("c", 3) in players[i]:
            current_player = i
            break
    last_play = None
    winner = None
    played_hand_image = None
    last_valid_player = None
    passed_players = []

# --------------------
# 設定選單與背景音樂控制
settings_mode = False  # 是否顯示設定選單
# 背景音樂音量（0.0 ~ 1.0）
bgm_volume = 0.5

# 載入背景音樂 (請確認 sounds 資料夾中有 bgm.mp3)
bgm_path = os.path.join("sounds", "bgm.mp3")
if os.path.exists(bgm_path):
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.set_volume(bgm_volume)
    pygame.mixer.music.play(-1)  # 迴圈播放

# 設定按鈕（右上角）
settings_button_rect = pygame.Rect(WIDTH - 120, 20, 100, 40)

# 設定選單內的滑軌參數
slider_bar_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 10, 300, 20)
slider_handle_rect = pygame.Rect(0, HEIGHT//2 - 15, 20, 30)
# 初始 handle 位置依 bgm_volume 設定
slider_handle_rect.x = slider_bar_rect.x + int(bgm_volume * (slider_bar_rect.width - slider_handle_rect.width))

dragging_slider = False

# --------------------
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
            if hand_type != check_hand_type(last_play) and hand_type not in {"four_of_a_kind", "straight_flush", "dragon", "flush_dragon"}:
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

        # 撥放對應牌型的音效，若無則撥放預設有效出牌音效
        if hand_type in hand_type_sounds and hand_type_sounds[hand_type]:
            hand_type_sounds[hand_type].play()
        elif valid_sound:
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

# --------------------
# 遊戲主迴圈
clock = pygame.time.Clock()
FPS = 60

# 一開始啟動一般發牌動畫（或使用 special_deal_flush_dragon()）
start_dealing()

running = True
while running:
    screen.fill(GREEN)
    positions = ["bottom", "left", "top", "right"]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                play_random_music()  # 按 M 切換音樂
            elif event.key == pygame.K_UP:
                volume = min(1.0, pygame.mixer.music.get_volume() + 0.1)
                pygame.mixer.music.set_volume(volume)
            elif event.key == pygame.K_DOWN:
                volume = max(0.0, pygame.mixer.music.get_volume() - 0.1)
                pygame.mixer.music.set_volume(volume)

    screen.fill((0, 128, 0))
    pygame.display.flip()

    # 先處理設定選單（背景音樂控制）
    if settings_mode:
        # 繪製半透明遮罩
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        # 繪製設定面板
        panel_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
        pygame.draw.rect(screen, GRAY, panel_rect)
        pygame.draw.rect(screen, DARKGRAY, panel_rect, 3)
        # 顯示標題
        font = pygame.font.SysFont(None, 36)
        title = font.render("設定", True, WHITE)
        screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        # 繪製背景音量滑軌
        pygame.draw.rect(screen, DARKGRAY, slider_bar_rect)
        pygame.draw.rect(screen, WHITE, slider_handle_rect)
        vol_text = font.render("背景音樂音量", True, WHITE)
        screen.blit(vol_text, (slider_bar_rect.x, slider_bar_rect.y - 30))
    
    # 如果正在發牌動畫，依照時間逐一建立動畫卡片
    if dealing_animation:
        current_time = pygame.time.get_ticks()
        if deal_order and current_time >= next_deal_time:
            player_index, card = deal_order.pop(0)
            target_pos = get_deal_target(player_index)
            animated_card = AnimatedCard(card, target_pos, player_index)
            animated_cards.append(animated_card)
            next_deal_time = current_time + 100  # 每 100 毫秒發一張
            if deal_sound:
                deal_sound.play()  # 撥放發牌音效

        # 更新動畫卡片
        for anim_card in animated_cards[:]:
            anim_card.update()
            if not anim_card.moving:
                # 卡片到達目標位置，加入玩家手牌
                players[anim_card.player_index].append(anim_card.card)
                animated_cards.remove(anim_card)

        # 發牌動畫結束判斷：若發牌順序與動畫卡片皆空，則完成發牌
        if not deal_order and not animated_cards:
            dealing_animation = False
            finalize_dealing()

    # 畫出各玩家的手牌
    for i, pos in enumerate(positions):
        card_positions = calculate_card_positions(players[i], pos)
        for j, card in enumerate(players[i]):
            card_image = card_images.get(card)
            if card_image:
                card_x, card_y = card_positions[j]
                # 若該玩家為目前出牌玩家，且該牌被選取，稍作偏移
                if i == current_player and card in selected_cards:
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

    # 畫出正在發牌動畫中的卡片（覆蓋於已發牌之上）
    if dealing_animation:
        for anim_card in animated_cards:
            anim_card.draw(screen)

    # 畫出最後出牌的牌型圖片
    if played_hand_image:
        image_rect = played_hand_image.get_rect(center=(WIDTH // 2 + 400, HEIGHT // 2 + 100))
        screen.blit(played_hand_image, image_rect)

    # 若有人獲勝，顯示勝利訊息
    if winner is not None:
        font = pygame.font.SysFont(None, 72)
        win_text = f"Player {winner+1} Wins!"
        text_surf = font.render(win_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text_surf, text_rect)

    # 畫出設定按鈕（只有在非設定模式下顯示）
    if not settings_mode:
        pygame.draw.rect(screen, DARKGRAY, settings_button_rect)
        font = pygame.font.SysFont(None, 24)
        btn_text = font.render("設定", True, WHITE)
        text_rect = btn_text.get_rect(center=settings_button_rect.center)
        screen.blit(btn_text, text_rect)

    pygame.display.flip()
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 若點擊設定按鈕，切換設定模式
            if not settings_mode:
                if settings_button_rect.collidepoint(event.pos):
                    settings_mode = True
                    continue
            # 在設定模式中處理滑軌拖曳
            if settings_mode:
                if slider_handle_rect.collidepoint(event.pos):
                    dragging_slider = True
            # 若非設定模式且非發牌動畫時，處理其他操作
            if not settings_mode and not dealing_animation and winner is None:
                if event.button == 1:
                    player_pos = positions[current_player]
                    hand_positions = calculate_card_positions(players[current_player], player_pos)
                    if player_pos in ["left", "right"]:
                        modified_hand_positions = [(x, y - 20) for (x, y) in hand_positions]
                    else:
                        modified_hand_positions = hand_positions
                    card_index = get_card_at_pos(pygame.mouse.get_pos(), modified_hand_positions)
                    if card_index is not None:
                        chosen_card = players[current_player][card_index]
                        if select_sound:
                            select_sound.play()
                        if chosen_card in selected_cards:
                            selected_cards.remove(chosen_card)
                        else:
                            selected_cards.append(chosen_card)

        elif event.type == pygame.MOUSEBUTTONUP:
            # 結束滑軌拖曳
            dragging_slider = False
            # 在設定模式中，若點擊遮罩外的面板外，則退出設定模式
            if settings_mode and not slider_bar_rect.collidepoint(event.pos):
                # 如果按下的是設定按鈕也忽略（不自動退出）
                if not settings_button_rect.collidepoint(event.pos):
                    settings_mode = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging_slider:
                # 更新滑軌 handle x 座標，限制在 slider_bar_rect 範圍內
                new_x = event.pos[0]
                new_x = max(slider_bar_rect.x, min(new_x, slider_bar_rect.x + slider_bar_rect.width - slider_handle_rect.width))
                slider_handle_rect.x = new_x
                # 根據 handle 位置計算新音量
                relative_pos = slider_handle_rect.x - slider_bar_rect.x
                bgm_volume = relative_pos / (slider_bar_rect.width - slider_handle_rect.width)
                pygame.mixer.music.set_volume(bgm_volume)

        elif event.type == pygame.KEYDOWN:
            if not settings_mode:
                if winner is not None:
                    if event.key == pygame.K_r:
                        start_dealing()
                        selected_cards.clear()
                else:
                    # F 鍵可直接指定特殊發牌（同花一條龍）
                    if event.key == pygame.K_f:
                        special_deal_flush_dragon()
                    elif event.key == pygame.K_RETURN:
                        play_selected_cards()
                    elif event.key == pygame.K_s:
                        pass_turn()
                    elif event.key == pygame.K_r:
                        start_dealing()
                        selected_cards.clear()
                        played_hand_image = None
            else:
                # 在設定模式下，按 Esc 鍵退出設定
                if event.key == pygame.K_ESCAPE:
                    settings_mode = False

pygame.quit()
