import pygame
import math


class Goal:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.world_x = x

    def draw(self, screen, camera_offset):
        # Draw a swirling portal using concentric rings and a pulsing inner circle
        draw_rect = pygame.Rect(self.rect.x - camera_offset, self.rect.y, self.rect.width, self.rect.height)
        cx = draw_rect.centerx
        cy = draw_rect.centery
        max_r = max(draw_rect.width, draw_rect.height) // 2

        # Pulsing factor
        t = pygame.time.get_ticks() / 400.0
        pulse = (math.sin(t) + 1) / 2

        # Outer rings
        for i in range(4, 0, -1):
            r = int(max_r * (i / 4.0))
            alpha = int(100 + 155 * (i / 4.0) * pulse)
            color = (80, 160, 255)
            # simple solid ring by drawing circle with width
            pygame.draw.circle(screen, color, (cx, cy), r, max(4, int(max_r*0.08)))

        # Inner core - animated swirl: draw rotating arcs
        for j in range(6):
            angle = t * 2 + j * (math.pi * 2 / 6)
            start_ang = angle
            end_ang = angle + math.pi / 3
            color = (120, 200, 255) if j % 2 == 0 else (60, 140, 220)
            pygame.draw.arc(screen, color, (cx - max_r//2, cy - max_r//2, max_r, max_r), start_ang, end_ang, 6)

        # Center glow
        inner_r = int(max_r * 0.25 + pulse * max_r * 0.15)
        pygame.draw.circle(screen, (180, 230, 255), (cx, cy), inner_r)
