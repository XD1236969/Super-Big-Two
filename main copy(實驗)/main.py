# main.py
import os
import random
import pygame
pygame.init()
pygame.mixer.init() 
import game_logic
import game_ui
import player

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("大老二 Big Two")

# 確保資源資料夾存在
os.makedirs("cards", exist_ok=True)
os.makedirs("hands", exist_ok=True)
os.makedirs("sounds", exist_ok=True)
os.makedirs("bgm", exist_ok=True)  # 新增背景音樂資料夾

# 初始化音效（注意：先初始化 mixer，再呼叫初始化音效）
game_ui.init_sounds()

# 背景音樂相關設定
def load_bgm_list():
    """讀取 bgm 資料夾內所有音樂檔案"""
    bgm_folder = "bgm"
    music_files = []
    for file in os.listdir(bgm_folder):
        if file.lower().endswith((".mp3", ".ogg", ".wav")):
            music_files.append(os.path.join(bgm_folder, file))
    return music_files

bgm_list = load_bgm_list()
current_bgm = None

def play_random_bgm():
    """隨機選一首背景音樂播放"""
    global current_bgm
    if bgm_list:
        current_bgm = random.choice(bgm_list)
        pygame.mixer.music.load(current_bgm)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

def play_next_bgm():
    """按下 M 時切換下一首背景音樂"""
    global current_bgm
    if bgm_list:
        # 選擇一首不同於目前播放的
        available = [m for m in bgm_list if m != current_bgm]
        if available:
            current_bgm = random.choice(available)
        else:
            current_bgm = random.choice(bgm_list)
        pygame.mixer.music.load(current_bgm)
        pygame.mixer.music.play(-1)

# 開始播放背景音樂
play_random_bgm()

# UI 相關參數（例如設定選單、滑軌）
settings_mode = False
slider_bar_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 10, 300, 20)
slider_handle_rect = pygame.Rect(0, HEIGHT//2 - 15, 20, 30)
bgm_volume = pygame.mixer.music.get_volume()
slider_handle_rect.x = slider_bar_rect.x + int(bgm_volume * (slider_bar_rect.width - slider_handle_rect.width))
settings_button_rect = pygame.Rect(WIDTH - 120, 20, 100, 40)
dragging_slider = False

clock = pygame.time.Clock()
FPS = 60

def play_random_music():
    """使用 M 鍵切換下一首背景音樂"""
    play_next_bgm()

# 開始發牌
game_logic.start_dealing()

running = True
while running:
    screen.fill((0,128,0))
    # 此處事件與繪圖邏輯與先前版本類似
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                play_random_music()
            elif event.key == pygame.K_UP:
                bgm_volume = min(1.0, pygame.mixer.music.get_volume() + 0.1)
                pygame.mixer.music.set_volume(bgm_volume)
            elif event.key == pygame.K_DOWN:
                bgm_volume = max(0.0, pygame.mixer.music.get_volume() - 0.1)
                pygame.mixer.music.set_volume(bgm_volume)
            # 其他按鍵事件…（例如出牌、過牌、重發牌等）
        # 滑鼠與其他事件也在這裡處理…
    
    # 畫面更新（清場、畫出玩家手牌、動畫、出牌圖片等）
    # 畫面上若有出牌圖片，會依照 game_logic 與 player.played_hand_image 顯示
    # （這部分可參照之前的主迴圈內容）
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
