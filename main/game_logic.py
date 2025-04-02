# game_logic.py
import os
import random
import pygame
pygame.init()
pygame.mixer.init()  # 先初始化 mixer
import math
from collections import Counter
import player
import game_ui

# 撲克牌基本資料與順序定義
suits = {"s": "黑桃", "h": "愛心", "d": "方塊", "c": "梅花"}
cards = [(suit, rank) for suit in suits.keys() for rank in range(1, 14)]
big_two_order = {3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 9, 13: 10, 1: 11, 2: 12}
suit_order = {"c": 0, "d": 1, "h": 2, "s": 3}

# 發牌動畫相關變數（供 main.py 使用）
dealing_animation = False
animated_cards = []   # 存放動畫中的 AnimatedCard 物件
deal_order = []       # (player_index, card) 的發牌順序
next_deal_time = 0

def check_hand_type(hand):
    """
    判斷手牌類型，包含一條龍與桐花一條龍
    """
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
        if len(set(suits_in_hand)) == 1:
            sorted_ranks = sorted(ranks)
            if sorted_ranks == list(range(sorted_ranks[0], sorted_ranks[0] + 5)):
                return "straight_flush"
        if 4 in count.values():
            return "four_of_a_kind"
        if sorted(count.values()) == [2, 3]:
            return "fullhouse"
        sorted_ranks = sorted(ranks)
        if sorted_ranks == list(range(sorted_ranks[0], sorted_ranks[0] + 5)):
            return "straight"
    return None

def hand_key(hand, hand_type):
    """
    根據牌型取得關鍵牌（決定牌組大小）
    """
    if hand_type in ["single", "pair", "triple", "straight", "straight_flush"]:
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

def compare_hands(new_hand, last_hand):
    """
    比較兩組牌的大小，包含 bomb 強壓功能
    """
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

def finalize_dealing():
    """
    發牌完成後，將各玩家手牌排序，並找出持有梅花3的玩家作為第一個出牌者
    """
    for i in range(4):
        player.players[i] = sorted(player.players[i], key=lambda x: (x[1], list(suits.keys()).index(x[0])))
        if ("c", 3) in player.players[i]:
            player.current_player = i

def start_dealing():
    """
    隨機洗牌後發牌，並建立發牌動畫的設定
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
    # 初始化本輪活躍玩家列表為所有玩家
    player.active_players = [0, 1, 2, 3]

def special_deal_flush_dragon():
    """
    特殊發牌：指定四家皆獲得同花一條龍
    """
    order = [3,4,5,6,7,8,9,10,11,12,13,1,2]
    player.players[0] = [("s", rank) for rank in order]
    player.players[1] = [("h", rank) for rank in order]
    player.players[2] = [("d", rank) for rank in order]
    player.players[3] = [("c", rank) for rank in order]
    for i in range(4):
        if ("c", 3) in player.players[i]:
            player.current_player = i
            break
    player.last_play = None
    player.winner = None
    player.last_valid_player = None
    player.passed_players = []
    player.active_players = [0, 1, 2, 3]

def play_selected_cards():
    """
    處理玩家出牌：
    - 檢查選牌是否合法，播放對應音效。
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

        # 載入出牌對應的牌型圖片（若存在）
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

        # 若出完牌則設為勝利者，否則換下一位出牌
        if len(player.players[player.current_player]) == 0:
            player.winner = player.current_player
        else:
            player.current_player = (player.current_player + 1) % 4

def pass_turn():
    """
    處理過牌：
    - 從本輪活躍玩家列表 (active_players) 中移除當前玩家。
    - 撥放跳過音效與顯示跳過圖片。
    - 當活躍玩家只剩下一位時，清空出牌限制並讓該玩家開始新一輪出牌，
      同時重置活躍玩家列表為所有玩家。
    - 否則，依照順時針移交出牌權。
    """
    # 從 active_players 中移除當前玩家（如果尚未被移除）
    if player.current_player in player.active_players:
        player.active_players.remove(player.current_player)

    if game_ui.skip_sound:
        game_ui.skip_sound.play()
    if game_ui.skip_image:
        player.played_hand_image = game_ui.skip_image

    # 如果本輪活躍玩家只剩下一人，表示其他三家都跳過
    if len(player.active_players) == 1:
        # 清空上一輪出牌限制
        player.last_play = None
        # 將出牌權交給這位活躍玩家
        player.current_player = player.active_players[0]
        # 重置本輪活躍玩家列表為所有玩家，開始新回合
        player.active_players = [0, 1, 2, 3]
    else:
        # 還有多於一位玩家活躍，則順時針移交出牌權
        player.current_player = (player.current_player + 1) % 4
