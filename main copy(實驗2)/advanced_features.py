# advanced_features.py
import random
import math
import pygame
from player import AIPlayer  # 假設 player 模組中已定義 AIPlayer
from game_logic import big_two_order, suit_order

# ---------------------------
# 進階 AI 對戰模式
# ---------------------------
class AdvancedAI(AIPlayer):
    """
    AdvancedAI 繼承自 AIPlayer，採用更精細的決策策略，
    可根據局勢選擇最佳出牌（此處僅為範例，可依需求進一步擴充）。
    """
    def __init__(self, name="AdvancedAI"):
        super().__init__(name)
    
    def decide_move(self, game_logic):
        # 模擬思考時間
        pygame.time.delay(300)
        # 如果手牌空則回傳 None
        if not self.hand:
            return None
        # 若沒有上家出牌，出最小單張
        if game_logic.last_hand is None:
            chosen = min(self.hand, key=lambda card: (big_two_order[card[1]], suit_order[card[0]]))
            self.hand.remove(chosen)
            return [chosen]
        # 有上家出牌，尋找能夠壓過的牌
        last_card = max(game_logic.last_hand, key=lambda card: (big_two_order[card[1]], suit_order[card[0]]))
        candidates = [
            card for card in self.hand
            if (big_two_order[card[1]], suit_order[card[0]]) >
               (big_two_order[last_card[1]], suit_order[last_card[0]])
        ]
        if candidates:
            chosen = min(candidates, key=lambda card: (big_two_order[card[1]], suit_order[card[0]]))
            self.hand.remove(chosen)
            return [chosen]
        return None  # 無法出牌則過牌

# ---------------------------
# 動態動畫與視覺特效
# ---------------------------
class ParticleEffect:
    """
    粒子特效，模擬例如勝利或特殊牌型時的閃爍、爆炸效果。
    
    :param pos: 特效產生的位置 (x, y)
    :param color: 粒子顏色 (RGB) 若為 None 表示每個粒子可隨機設定顏色
    :param duration: 持續時間（毫秒）
    :param particle_count: 粒子數量
    """
    def __init__(self, pos, color, duration=1000, particle_count=50):
        self.pos = pos
        self.color = color
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.particles = []
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            # 如果 color 為 None，則隨機生成顏色
            p_color = color if color is not None else (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            self.particles.append({
                "pos": list(pos),
                "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
                "radius": random.randint(2, 4),
                "color": p_color
            })
    
    def update(self):
        current_time = pygame.time.get_ticks()
        # 檢查是否超過持續時間
        if current_time - self.start_time > self.duration:
            self.particles = []
        # 更新每個粒子的位置與大小（模擬逐漸消失）
        for p in self.particles:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["radius"] = max(0, p["radius"] - 0.05)
    
    def draw(self, surface):
        for p in self.particles:
            if p["radius"] > 0:
                pygame.draw.circle(surface, p["color"], (int(p["pos"][0]), int(p["pos"][1])), int(p["radius"]))

def update_particle_effects(effects):
    """
    更新並移除已結束的粒子特效
    :param effects: 粒子特效列表
    """
    for effect in effects:
        effect.update()
    effects[:] = [effect for effect in effects if effect.particles]
from particle_effects import ParticleEffectManager

particle_manager = ParticleEffectManager()

def trigger_special_effect(pos, color=(255, 215, 0), duration=1000, particle_count=100):
    return particle_manager.trigger_effect(pos, color, duration, particle_count)

def trigger_hand_effect(hand_type, pos):
    """
    根據牌型觸發對應的特效
    
    :param hand_type: 牌型名稱，可能值有 "straight", "fullhouse", "four_of_a_kind",
                      "straight_flush", "dragon", "flush_dragon"
    :param pos: 特效觸發位置 (x, y)
    :return: ParticleEffect 物件或 None
    """
    if hand_type == "straight":
        effect = trigger_special_effect(pos, color=(0, 255, 0))
    elif hand_type == "fullhouse":
        effect = trigger_special_effect(pos, color=(0, 0, 255))
    elif hand_type == "four_of_a_kind":
        effect = trigger_special_effect(pos, color=(255, 0, 0))
    elif hand_type == "straight_flush":
        effect = trigger_special_effect(pos, color=(255, 215, 0))
    elif hand_type == "dragon":
        # 彩色效果：每個粒子隨機設定顏色
        effect = trigger_special_effect(pos, color=None)
    elif hand_type == "flush_dragon":
        # 更強大的彩色效果：增加粒子數量與顏色變化
        effect = trigger_special_effect(pos, color=None, particle_count=150)
    else:
        effect = None
    return effect

def trigger_center_effect(surface, color=(255, 215, 0), duration=1000, particle_count=100):
    """
    從畫面中央向外發射粒子
    
    :param surface: 畫面物件，從中取得中央座標
    :param color: 粒子顏色，預設為金色；若為 None 則每個粒子隨機設定顏色
    :param duration: 特效持續時間（毫秒）
    :param particle_count: 粒子數量
    :return: ParticleEffect 物件
    """
    center = surface.get_rect().center
    return trigger_special_effect(center, color=color, duration=duration, particle_count=particle_count)

# ---------------------------
# AI 模式開關元件
# ---------------------------
class AISwitch:
    """
    簡單的切換按鈕，用於控制 AI 模式的開啟與關閉，
    在畫面上顯示一個按鈕，點擊後改變狀態。
    """
    def __init__(self, pos, size=(100, 40), initial_state=True):
        self.rect = pygame.Rect(pos, size)
        self.state = initial_state  # True 表示 AI 模式啟用，False 表示停用
        self.font = pygame.font.SysFont(None, 24)
    
    def draw(self, surface):
        # 根據狀態改變顏色：綠色表示啟用，紅色表示停用
        color = (0, 200, 0) if self.state else (200, 0, 0)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        text = "AI ON" if self.state else "AI OFF"
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """
        處理滑鼠事件，點擊開關時切換狀態。
        :return: 若狀態改變，則回傳 True；否則回傳 False
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state
                return True
        return False
