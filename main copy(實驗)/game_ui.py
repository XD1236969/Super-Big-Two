# game_ui.py
import os
import pygame
import math

# 遊戲視窗尺寸與卡牌相關尺寸
WIDTH, HEIGHT = 800, 600
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_SPACING = 20
CARD_Y = HEIGHT - CARD_HEIGHT + 190
CARD_OFFSET_X = 350

# 色彩設定
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)

# 載入牌面圖片
def load_card_image(suit, rank):
    path = os.path.join("cards", f"{suit}{rank}.jpg")
    return pygame.image.load(path) if os.path.exists(path) else None

suits = {"s": "黑桃", "h": "愛心", "d": "方塊", "c": "梅花"}
card_images = {(suit, rank): load_card_image(suit, rank)
               for suit in suits.keys() for rank in range(1, 14)}

# 載入音效
def load_sound(filename):
    path = os.path.join("sounds", filename)
    return pygame.mixer.Sound(path) if os.path.exists(path) else None

valid_sound = load_sound("valid.wav")
invalid_sound = load_sound("invalid.wav")
skip_sound = load_sound("skip.wav")
deal_sound = load_sound("deal.wav")
select_sound = load_sound("select.wav")

# 各牌型專屬音效（包含一條龍與桐花一條龍）
hand_type_sounds = {
    "single": load_sound("single.wav"),
    "pair": load_sound("pair.wav"),
    "triple": load_sound("triple.wav"),
    "straight": load_sound("straight.wav"),
    "fullhouse": load_sound("fullhouse.wav"),
    "four_of_a_kind": load_sound("four_of_a_kind.wav"),
    "straight_flush": load_sound("straight_flush.wav"),
    "dragon": load_sound("dragon.wav"),
    "flush_dragon": load_sound("flush_dragon.wav")
}

# 載入手牌圖片（放在 hands 資料夾）
hand_type_images = {
    "single": "single.png",
    "pair": "pair.png",
    "triple": "triple.png",
    "straight": "straight.png",
    "fullhouse": "fullhouse.png",
    "four_of_a_kind": "four_of_a_kind.png",
    "straight_flush": "straight_flush.png",
    "dragon": "dragon.png",
    "flush_dragon": "flush_dragon.png"
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

# 載入跳過圖片（若存在）
skip_image_path = os.path.join("hands", "skip.png")
skip_image = pygame.image.load(skip_image_path) if os.path.exists(skip_image_path) else None

def calculate_card_positions(hand, position):
    """
    根據玩家位置計算手牌的擺放位置
    """
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

def get_card_at_pos(pos, hand_positions):
    """
    根據滑鼠點擊座標判斷點擊到哪一張牌
    """
    for i, (x, y) in enumerate(hand_positions):
        if x <= pos[0] <= x + CARD_WIDTH and y <= pos[1] <= y + CARD_HEIGHT:
            return i
    return None

def get_deal_target(player_index):
    """
    取得指定玩家發牌動畫的目標位置
    """
    positions_names = ["bottom", "left", "top", "right"]
    pos_name = positions_names[player_index]
    hand_count = len(__import__("player").player.players[player_index]) if False else 0
    # 以 dummy list 模擬新增一張牌
    dummy_hand = [None] * (hand_count + 1)
    card_positions = calculate_card_positions(dummy_hand, pos_name)
    return card_positions[-1]

class AnimatedCard:
    """
    發牌動畫中的卡牌類別
    """
    def __init__(self, card, target_pos, player_index):
        self.card = card
        self.player_index = player_index
        self.x, self.y = WIDTH // 2, HEIGHT // 2  # 起始位置：螢幕中央
        self.target_x, self.target_y = target_pos
        self.angle = 0
        self.speed = 15
        self.rotation_speed = 5
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

def draw(surface):
    """
    畫面繪製輔助函式（可依需求擴充）
    """
    surface.fill(GREEN)

def setup_bgm():
    """
    載入並播放背景音樂
    """
    bgm_path = os.path.join("sounds", "bgm.mp3")
    if os.path.exists(bgm_path):
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
