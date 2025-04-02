# player.py

# 每位玩家的手牌（四個玩家）
players = [[], [], [], []]

# 當前玩家編號（預設 0）
current_player = 0

# 當前選取的牌（出牌前的暫存）
selected_cards = []

# 紀錄上一家成功出牌的牌組
last_play = None

# 勝利者（若有玩家出完牌則記錄玩家編號）
winner = None

# 紀錄最後成功出牌的玩家
last_valid_player = None

# 本輪已過牌玩家列表（舊機制，可保留作參考）
passed_players = []

# 最後出牌所對應的牌型圖片（供顯示用）
played_hand_image = None

# 新增：本輪活躍玩家列表，初始時所有玩家都參與
active_players = [0, 1, 2, 3]
