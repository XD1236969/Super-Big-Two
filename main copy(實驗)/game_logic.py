# game_logic.py
# ...（前面的程式碼保持不變）

def start_dealing():
    """
    隨機洗牌後發牌，建立發牌動畫設定，
    同時清除畫面上所有與上次遊戲相關的圖片（清場功能）
    """
    global dealing_animation, animated_cards, deal_order, next_deal_time
    random.shuffle(cards)
    player.players = [ [] for _ in range(4) ]
    dealing_animation = True
    animated_cards = []
    deal_order = []
    card_index = 0
    for r in range(13):
        for p in range(4):
            deal_order.append( (p, cards[card_index]) )
            card_index += 1
    next_deal_time = pygame.time.get_ticks() + 100
    player.last_play = None
    player.winner = None
    player.last_valid_player = None
    player.passed_players = []
    player.active_players = [0, 1, 2, 3]
    # 清除畫面上顯示的圖片（例如上次出牌的圖片）
    player.played_hand_image = None

def play_selected_cards():
    """
    處理玩家出牌：
    - 檢查選牌是否合法，播放對應音效。
    - 若是 bomb 牌型則除了常規處理外，另外將 bomb 圖片顯示在畫面中間偏右。
    - 更新出牌狀態，並從玩家手牌中移除已出的牌。
    """
    if player.selected_cards:
        hand_type = check_hand_type(player.selected_cards)
        if hand_type is None:
            if game_ui.invalid_sound:
                game_ui.invalid_sound.play()
            return

        # 第一回合必須包含梅花3
        if player.last_play is None:
            if ("c", 3) not in player.selected_cards:
                if game_ui.invalid_sound:
                    game_ui.invalid_sound.play()
                return

        # 非第一回合必須與上一家牌型相同且比其大，除非 bomb 強壓
        if player.last_play is not None:
            if hand_type != check_hand_type(player.last_play) and hand_type not in {"four_of_a_kind", "straight_flush", "dragon", "flush_dragon"}:
                if game_ui.invalid_sound:
                    game_ui.invalid_sound.play()
                return
            if not compare_hands(player.selected_cards, player.last_play):
                if game_ui.invalid_sound:
                    game_ui.invalid_sound.play()
                return

        # 合法出牌：更新 last_play 與 last_valid_player
        player.last_play = player.selected_cards.copy()
        player.last_valid_player = player.current_player

        # 播放對應音效
        if hand_type in game_ui.hand_type_sounds and game_ui.hand_type_sounds[hand_type]:
            game_ui.hand_type_sounds[hand_type].play()
        elif game_ui.valid_sound:
            game_ui.valid_sound.play()

        # 若是 bomb 牌型，除了正常處理外，另外顯示 bomb 圖片
        if hand_type in {"four_of_a_kind", "straight_flush", "dragon", "flush_dragon"}:
            bomb_image_path = os.path.join("hands", "bomb.png")
            if os.path.exists(bomb_image_path):
                bomb_image = pygame.image.load(bomb_image_path)
                orig_rect = bomb_image.get_rect()
                new_size = (int(orig_rect.width * 0.7), int(orig_rect.height * 0.7))
                player.played_hand_image = pygame.transform.smoothscale(bomb_image, new_size)
            else:
                player.played_hand_image = None
        else:
            # 載入一般牌型的圖片
            if hand_type in game_ui.hand_type_images:
                image_path = os.path.join("hands", game_ui.hand_type_images[hand_type])
                if os.path.exists(image_path):
                    played_image = pygame.image.load(image_path)
                    orig_rect = played_image.get_rect()
                    new_size = (int(orig_rect.width * 0.7), int(orig_rect.height * 0.7))
                    player.played_hand_image = pygame.transform.smoothscale(played_image, new_size)
                else:
                    player.played_hand_image = None
            else:
                player.played_hand_image = None

        # 從玩家手牌中移除出牌的卡牌
        for card in player.selected_cards:
            if card in player.players[player.current_player]:
                player.players[player.current_player].remove(card)
        player.selected_cards.clear()
        player.passed_players = []  # 舊機制清空

        # 檢查是否有人出完牌
        if len(player.players[player.current_player]) == 0:
            player.winner = player.current_player
        else:
            player.current_player = (player.current_player + 1) % 4
