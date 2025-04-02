# hand_display.py
import os
import pygame

def load_hand_card_image(suit, rank):
    """
    從 hands 資料夾載入對應的牌面圖片
    預設檔名格式：{suit}{rank}.png
    """
    filename = f"{suit}{rank}.png"
    path = os.path.join("hands", filename)
    if os.path.exists(path):
        try:
            return pygame.image.load(path)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
    else:
        print(f"Image not found: {path}")
    return None

def display_hand_cards(surface, cards, start_pos=(0, 10), spacing=10, card_size=None):
    """
    在指定 surface 上，從 start_pos 位置開始依序排列顯示 cards 列表中的卡片圖片。
    
    參數:
      surface: pygame 的顯示畫面
      cards: 牌組列表，每個元素為 (suit, rank) 例如: [("c", 3), ("d", 4), ...]
      start_pos: 起始顯示位置，預設為 (0, 10)
      spacing: 每張牌之間的水平間距，預設為 10 像素
      card_size: 若提供 (width, height)，則將圖片縮放到該尺寸；預設為 None（不縮放）
    """
    x, y = start_pos
    for card in cards:
        suit, rank = card
        image = load_hand_card_image(suit, rank)
        if image:
            if card_size:
                image = pygame.transform.smoothscale(image, card_size)
            surface.blit(image, (x, y))
            # 使用提供的寬度或圖片原始寬度來計算下一張牌的 x 座標
            width = card_size[0] if card_size else image.get_width()
            x += width + spacing
