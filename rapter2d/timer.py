import pygame


class CooldownTimer:
    def __init__(self, cooldown_ms: int) -> None:
        self.cooldown_ms = cooldown_ms
        self.last_trigger_time = 0
    
    def ready(self) -> bool:
        current_time = pygame.time.get_ticks()
        return (current_time - self.last_trigger_time) >= self.cooldown_ms

    def trigger(self) -> None:
        self.last_trigger_time = pygame.time.get_ticks()
