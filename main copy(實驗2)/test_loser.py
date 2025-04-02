# test_loser.py
import os
import pygame

def show_loser_image(surface, pos=(0, 0), size=None):
    """
    從 hands 資料夾讀取 loser.png，並在指定的 surface 上的 pos 位置顯示出來。
    若提供 size (width, height)，則圖片會被縮放到該尺寸。
    """
    path = os.path.join("hands", "loser.png")
    if os.path.exists(path):
        try:
            image = pygame.image.load(path)
            if size:
                image = pygame.transform.smoothscale(image, size)
            surface.blit(image, pos)
        except Exception as e:
            print(f"Error loading loser.png: {e}")
    else:
        print("loser.png not found in the hands folder.")
