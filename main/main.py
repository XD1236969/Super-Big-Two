# main.py
import os
import pygame
pygame.init()
pygame.mixer.init()  # 在載入其他模組前初始化 mixer
import game_logic
import player
import game_ui

# 初始化 Pygame 與 Mixer
pygame.init()
pygame.mixer.init()

# 遊戲視窗與基本設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("大老二 Big Two")

# 確保資源資料夾存在
os.makedirs("cards", exist_ok=True)
os.makedirs("hands", exist_ok=True)
os.makedirs("sounds", exist_ok=True)

# 設定背景色（例如綠色桌布）
GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARKGRAY = (100, 100, 100)
WHITE = (255, 255, 255)

# 設定背景音樂 (由 game_ui 提供)
game_ui.setup_bgm()
bgm_volume = pygame.mixer.music.get_volume()

# UI 相關：設定選單與滑軌參數
settings_mode = False
slider_bar_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 10, 300, 20)
slider_handle_rect = pygame.Rect(0, HEIGHT//2 - 15, 20, 30)
# 初始 handle 位置依現行音量設定
slider_handle_rect.x = slider_bar_rect.x + int(bgm_volume * (slider_bar_rect.width - slider_handle_rect.width))
settings_button_rect = pygame.Rect(WIDTH - 120, 20, 100, 40)
dragging_slider = False

# 時間控制
clock = pygame.time.Clock()
FPS = 60

# 若要切換音樂，可自行實作此函式（此處僅為範例）
def play_random_music():
    # 可加入隨機切換背景音樂的邏輯
    pass

# 開始發牌（包含發牌動畫）
game_logic.start_dealing()

# 遊戲主迴圈
running = True
while running:
    # 每次迴圈先填滿背景色
    screen.fill(GREEN)
    positions = ["bottom", "left", "top", "right"]

    # 處理事件（注意：部分事件在下方再次處理）
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 鍵盤事件
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                play_random_music()  # 按 M 切換音樂（範例函式）
            elif event.key == pygame.K_UP:
                bgm_volume = min(1.0, pygame.mixer.music.get_volume() + 0.1)
                pygame.mixer.music.set_volume(bgm_volume)
            elif event.key == pygame.K_DOWN:
                bgm_volume = max(0.0, pygame.mixer.music.get_volume() - 0.1)
                pygame.mixer.music.set_volume(bgm_volume)
            elif not settings_mode:
                if player.winner is not None:
                    if event.key == pygame.K_r:
                        game_logic.start_dealing()
                        player.selected_cards.clear()
                else:
                    # F 鍵可特殊發牌（同花一條龍）
                    if event.key == pygame.K_f:
                        game_logic.special_deal_flush_dragon()
                    elif event.key == pygame.K_RETURN:
                        game_logic.play_selected_cards()
                    elif event.key == pygame.K_s:
                        game_logic.pass_turn()
                    elif event.key == pygame.K_r:
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
                    # 根據目前玩家位置計算手牌位置（若為左右側，可略微調整）
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
                bgm_volume = relative_pos / (slider_bar_rect.width - slider_handle_rect.width)
                pygame.mixer.music.set_volume(bgm_volume)

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
