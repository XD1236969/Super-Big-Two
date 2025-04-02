import os
import random
import pygame
import keyboard  # 新增 keyboard 模組

# 初始化 pygame 與 mixer（必須在導入其他模組前初始化）
pygame.init()
pygame.mixer.init()

# 載入其他模組
import main as old_main  
import game_logic
import player
import game_ui
import advanced_features
import hand_display
import test_loser  # 測試模組

def run_game():
    """
    主循環：
      - 按下空白鍵觸發 advanced_features 的粒子效果
      - 按下 L 鍵觸發 loser 效果 (非勝利者顯示 loser.png 並播放 loser.wav 3 次)
      - 按下 P 鍵觸發 played_hand_visual，根據玩家打出的牌型在 (0,10) 位置顯示牌型圖片
      - 按下 ENTER 鍵觸發 hand_display 模組，依據 player.selected_cards 讀取圖片排列顯示在 (0,10)
      - 按下 ESCAPE 鍵時，使用 test_loser 模組在畫面上生成 hands 資料夾裡的 loser.png
    """
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
    
    # 背景音樂設定
    bgm_folder = os.path.join("sounds", "bgm")
    if os.path.isdir(bgm_folder):
        bgm_files = [os.path.join(bgm_folder, f) for f in os.listdir(bgm_folder) if f.endswith(".mp3")]
        if bgm_files:
            chosen = random.choice(bgm_files)
            pygame.mixer.music.load(chosen)
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(-1)
            print(f"Playing background music: {chosen}")

    # 初始化畫面與時鐘
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Advanced Features Demo")
    clock = pygame.time.Clock()

    # 儲存粒子特效物件
    particle_effects = []

    running = True
    while running:
        print("AAA")
        # 檢查 o 鍵是否被按下
        if keyboard.is_pressed("o"):
            print("o pressed! Displaying loser image from test_loser module...")
            test_loser.show_loser_image(screen, pos=(100, 100), size=(100, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("SPACE pressed! Triggering particle effect.")
                    effect = advanced_features.trigger_center_effect(
                        screen, color=(255, 215, 0), duration=1500, particle_count=120
                    )
                    particle_effects.append(effect)
                    success = game_logic.game.play_cards(game_logic.player)
                    if success:
                        print("牌型打出，畫面更新！")
                
                elif event.key == pygame.K_l:
                    print("L pressed! Triggering loser effect...")
                    game_ui.show_loser_effects(screen, winner=0)
                    
                elif event.key == pygame.K_p:
                    print("P pressed! Displaying played hand visual...")
                    
                elif event.key == pygame.K_RETURN:
                    print("ENTER pressed! Displaying hand with hand_display module...")
                    hand_display.display_hand_cards(screen, player.selected_cards, start_pos=(0,10), spacing=5, card_size=(50,75))
                
                elif event.key == pygame.K_o:
                    print("O pressed! Displaying loser image from test_loser module...")
                    test_loser.show_loser_image(screen, pos=(100, 100), size=(100, 100))
                elif event.key == pygame.K_ESCAPE:
                    print("ESCAPE pressed! Showing loser image...")
                    game_ui.show_loser_effects(screen, winner=1)  # 設定 winner 為 1

        advanced_features.update_particle_effects(particle_effects)
        screen.fill((0, 0, 0))
        for effect in particle_effects:
            effect.draw(screen)
            
        pygame.display.flip()
        clock.tick(60)

        if game_logic.game_over():
            winner = player.get_winner()
            print(f"Game over! Winner is Player {winner}")
            game_ui.show_loser_effects(screen, winner=winner)
            running = False

    pygame.quit()

if __name__ == '__main__':
    run_game()
    
