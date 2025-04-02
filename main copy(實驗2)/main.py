#main.py
import os
import random
import pygame
pygame.init()
pygame.mixer.init()  # 在載入其他模組前初始化 mixer
import game_logic
import player
import game_ui

# 遊戲視窗與基本設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("大老二 Big Two")

# 確保資源資料夾存在
os.makedirs("cards", exist_ok=True)
os.makedirs("hands", exist_ok=True)
os.makedirs("sounds", exist_ok=True)
os.makedirs("sounds/bgm", exist_ok=True)  # 新增背景音樂資料夾

# 色彩設定
GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARKGRAY = (100, 100, 100)
WHITE = (255, 255, 255)

# ---------------------------
# 隨機背景音樂相關設定
# 將所有 sounds/bgm 資料夾內的 mp3 檔案讀進 bgm_files
bgm_folder = os.path.join("sounds", "bgm")
bgm_files = [os.path.join(bgm_folder, f) for f in os.listdir(bgm_folder) if f.endswith(".mp3")]


def main():
    print("BBB")
    # 初始化 Pygame 與視窗
    pygame.init()
    pygame.mixer.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("大老二 Big Two")
    clock = pygame.time.Clock()

    # 建立遊戲邏輯與玩家
    game_logic = GameLogic()
    # 玩家陣容：玩家0為人類，其餘為 AI
    players = [HumanPlayer("Player"), AIPlayer("AI_1"), AIPlayer("AI_2"), AIPlayer("AI_3")]
    deal_cards(players, game_logic.cards)  # 將牌依序發給各玩家
    # 更新 game_logic 的玩家手牌紀錄
    game_logic.players_cards = [p.hand for p in players]

    # 建立 UI 物件（包含動畫管理）
    game_ui = GameUI(screen, game_logic, players)

    running = True
    while running:
        print("BBB")
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # 交由 UI 處理玩家事件（例如選牌）
            game_ui.handle_event(event)
        
        # 當前玩家輪到 AI 時，自動決策出牌
        current_index = game_logic.current_player
        current_player = players[current_index]
        if isinstance(current_player, AIPlayer):
            pygame.time.delay(500)  # 模擬 AI 思考時間
            move = current_player.decide_move(game_logic)
            game_logic.play_move(move)
        # 若為人類玩家，則等待事件觸發（例如按下確認鍵出牌）
        
        game_logic.update()  # 檢查遊戲狀態（例如是否有人出完牌）
        update_animations(game_ui.animations, dt)
        game_ui.draw()     # 繪製畫面與動畫
        pygame.display.flip()

        
def play_random_music():
    if bgm_files:
        chosen = random.choice(bgm_files)
        pygame.mixer.music.load(chosen)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        print(f"Playing: {chosen}")

def next_music():
    # 隨機切換下一首
    if bgm_files:
        chosen = random.choice(bgm_files)
        pygame.mixer.music.load(chosen)
        pygame.mixer.music.play(-1)
        print(f"Switched to: {chosen}")

# 初始播放背景音樂
play_random_music()
# ---------------------------

# UI 相關：設定選單與滑軌參數
settings_mode = False
slider_bar_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 10, 300, 20)
slider_handle_rect = pygame.Rect(0, HEIGHT//2 - 15, 20, 30)
# 初始 handle 位置依現行音量設定
slider_handle_rect.x = slider_bar_rect.x + int(pygame.mixer.music.get_volume() * (slider_bar_rect.width - slider_handle_rect.width))
settings_button_rect = pygame.Rect(WIDTH - 120, 20, 100, 40)
dragging_slider = False

# 時間控制
clock = pygame.time.Clock()
FPS = 60

# 新增：清場函式，重新發牌時清除畫面上最後出牌的圖片與狀態
def clear_board():
    player.played_hand_image = None
    player.last_play = None

# 若要切換音樂，可自行實作此函式（此處以 next_music 為例）
def play_selected_cards_wrapper():
    # 呼叫遊戲邏輯的出牌處理，內部會印出 debug 資訊
    game_logic.play_selected_cards()

# 開始發牌（包含發牌動畫）
game_logic.start_dealing()

# 遊戲主迴圈
running = True
positions = ["bottom", "left", "top", "right"]
while running:
    screen.fill(GREEN)

    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 鍵盤事件
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                next_music()  # 按 M 切換至下一首背景音樂
            elif event.key == pygame.K_UP:
                vol = min(1.0, pygame.mixer.music.get_volume() + 0.1)
                pygame.mixer.music.set_volume(vol)
            elif event.key == pygame.K_DOWN:
                vol = max(0.0, pygame.mixer.music.get_volume() - 0.1)
                pygame.mixer.music.set_volume(vol)
            elif not settings_mode:
                if player.winner is not None:
                    if event.key == pygame.K_r:
                        clear_board()
                        game_logic.start_dealing()
                        player.selected_cards.clear()
                else:
                    # F 鍵可特殊發牌（同花一條龍）
                    if event.key == pygame.K_f:
                        game_logic.special_deal_flush_dragon()
                    elif event.key == pygame.K_RETURN:
                        play_selected_cards_wrapper()
                    elif event.key == pygame.K_s:
                        game_logic.pass_turn()
                    elif event.key == pygame.K_r:
                        clear_board()  # 重新發牌前清除畫面
                        game_logic.start_dealing()
                        player.selected_cards.clear()
            else:
                if event.key == pygame.K_ESCAPE:
                    settings_mode = False

        # 滑鼠事件：點擊、拖曳等
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 點擊設定按鈕進入設定模式（若尚未在設定模式中）
            if not settings_mode:
                if settings_button_rect.collidepoint(event.pos):
                    settings_mode = True
                    continue
            # 在設定模式中，檢查是否點擊滑軌 handle
            if settings_mode:
                if slider_handle_rect.collidepoint(event.pos):
                    dragging_slider = True
            # 若非設定模式且非發牌動畫時，處理出牌選取
            if not settings_mode and not game_logic.dealing_animation and player.winner is None:
                # 以左鍵點擊來選取或取消選牌
                if event.button == 1:
                    player_pos = positions[player.current_player]
                    hand_positions = game_ui.calculate_card_positions(player.players[player.current_player], player_pos)
                    if player_pos in ["left", "right"]:
                        modified_hand_positions = [(x, y - 20) for (x, y) in hand_positions]
                    else:
                        modified_hand_positions = hand_positions
                    card_index = game_ui.get_card_at_pos(pygame.mouse.get_pos(), modified_hand_positions)
                    if card_index is not None:
                        chosen_card = player.players[player.current_player][card_index]
                        if game_ui.select_sound:
                            game_ui.select_sound.play()
                        if chosen_card in player.selected_cards:
                            player.selected_cards.remove(chosen_card)
                        else:
                            player.selected_cards.append(chosen_card)

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_slider = False
            if settings_mode and not slider_bar_rect.collidepoint(event.pos):
                if not settings_button_rect.collidepoint(event.pos):
                    settings_mode = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging_slider:
                new_x = event.pos[0]
                new_x = max(slider_bar_rect.x, min(new_x, slider_bar_rect.x + slider_bar_rect.width - slider_handle_rect.width))
                slider_handle_rect.x = new_x
                relative_pos = slider_handle_rect.x - slider_bar_rect.x
                vol = relative_pos / (slider_bar_rect.width - slider_handle_rect.width)
                pygame.mixer.music.set_volume(vol)

    # 若正在發牌動畫，依照時間逐一建立動畫卡片
    if game_logic.dealing_animation:
        current_time = pygame.time.get_ticks()
        if game_logic.deal_order and current_time >= game_logic.next_deal_time:
            player_index, card = game_logic.deal_order.pop(0)
            target_pos = game_ui.get_deal_target(player_index)
            animated_card = game_ui.AnimatedCard(card, target_pos, player_index)
            game_logic.animated_cards.append(animated_card)
            game_logic.next_deal_time = current_time + 100  # 每 100 毫秒發一張
            if game_ui.deal_sound:
                game_ui.deal_sound.play()

        # 更新動畫卡片
        for anim_card in game_logic.animated_cards[:]:
            anim_card.update()
            if not anim_card.moving:
                player.players[anim_card.player_index].append(anim_card.card)
                game_logic.animated_cards.remove(anim_card)
        # 發牌動畫結束判斷：若發牌順序與動畫皆空，完成發牌
        if not game_logic.deal_order and not game_logic.animated_cards:
            game_logic.dealing_animation = False
            game_logic.finalize_dealing()

    # 畫出各玩家的手牌
    for i, pos in enumerate(positions):
        card_positions = game_ui.calculate_card_positions(player.players[i], pos)
        for j, card in enumerate(player.players[i]):
            card_image = game_ui.card_images.get(card)
            if card_image:
                card_x, card_y = card_positions[j]
                # 若為目前出牌玩家且該牌被選中，則稍作偏移
                if i == player.current_player and card in player.selected_cards:
                    if pos == "bottom":
                        card_y -= 20
                    elif pos == "top":
                        card_y += 20
                    elif pos == "left":
                        card_x += 20
                    elif pos == "right":
                        card_x -= 20
                scaled_card = pygame.transform.scale(card_image, (game_ui.CARD_WIDTH, game_ui.CARD_HEIGHT))
                screen.blit(scaled_card, (card_x, card_y))

    # 畫出正在發牌動畫中的卡片（若有）
    if game_logic.dealing_animation:
        for anim_card in game_logic.animated_cards:
            anim_card.draw(screen)

    # 畫出最後出牌的牌型圖片（若有）
    if player.played_hand_image:
        image_rect = player.played_hand_image.get_rect(center=(WIDTH // 2 + 400, HEIGHT // 2 + 100))
        screen.blit(player.played_hand_image, image_rect)

    # 若有人獲勝，顯示勝利訊息
    if player.winner is not None:
        font = pygame.font.SysFont(None, 72)
        win_text = f"Player {player.winner+1} Wins!"
        text_surf = font.render(win_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text_surf, text_rect)

    # 畫出設定按鈕（非設定模式下）
    if not settings_mode:
        pygame.draw.rect(screen, DARKGRAY, settings_button_rect)
        font = pygame.font.SysFont(None, 24)
        btn_text = font.render("設定", True, WHITE)
        text_rect = btn_text.get_rect(center=settings_button_rect.center)
        screen.blit(btn_text, text_rect)

    # 若在設定模式，畫出半透明遮罩與設定面板
    if settings_mode:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
        pygame.draw.rect(screen, GRAY, panel_rect)
        pygame.draw.rect(screen, DARKGRAY, panel_rect, 3)
        font = pygame.font.SysFont(None, 36)
        title = font.render("設定", True, WHITE)
        screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        pygame.draw.rect(screen, DARKGRAY, slider_bar_rect)
        pygame.draw.rect(screen, WHITE, slider_handle_rect)
        vol_text = font.render("背景音樂音量", True, WHITE)
        screen.blit(vol_text, (slider_bar_rect.x, slider_bar_rect.y - 30))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
