#particle_effects.py
import random
import math
import pygame

class ParticleEffect:
    def __init__(self, pos, color=None, duration=1000, particle_count=50):
        self.pos = pos
        self.color = color
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.particles = []
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            self.particles.append({
                "pos": list(pos),
                "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
                "radius": random.randint(2, 4),
                "color": color if color else [random.randint(0, 255) for _ in range(3)]
            })

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.particles = []

        for p in self.particles:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["radius"] = max(0, p["radius"] - 0.05)

    def draw(self, surface):
        for p in self.particles:
            if p["radius"] > 0:
                pygame.draw.circle(surface, p["color"], (int(p["pos"][0]), int(p["pos"][1])), int(p["radius"]))

    def is_finished(self):
        return len(self.particles) == 0


class ParticleEffectManager:
    def __init__(self):
        self.effects = []

    def trigger_effect(self, pos, color=None, duration=1000, particle_count=100):
        effect = ParticleEffect(pos, color, duration, particle_count)
        self.effects.append(effect)

    def update(self):
        for effect in self.effects:
            effect.update()
        self.effects = [effect for effect in self.effects if not effect.is_finished()]

    def draw(self, surface):
        for effect in self.effects:
            effect.draw(surface)
