import pygame
import settings
from config import GRAVITY
import math


class Player:
    def __init__(self, x, y, width=30, height=60):
        scale_x = settings.get_width_ratio()
        scale_y = settings.get_height_ratio()

        self.rect = pygame.Rect(x, y, width * scale_x, height * scale_y)
        self.x = x
        self.vel_y = 0
        self.on_ground = False
        self.prev_x = x
        self.facing = 'right'
        self.moving = False

    def jump(self):
        if self.on_ground:
            self.vel_y = -settings.get_jump_speed()
            self.on_ground = False

    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

    def update(self, platforms):
        self.apply_gravity()
        self.check_collision(platforms)
        # update movement state for simple animation
        dx = self.x - getattr(self, 'prev_x', self.x)
        if abs(dx) > 0.5:
            self.moving = True
            self.facing = 'right' if dx > 0 else 'left'
        else:
            self.moving = False
        self.prev_x = self.x

    def check_collision(self, platforms):
        self.on_ground = False
        for platform in platforms:
            if self.get_rect().colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True

    def get_rect(self):
        return pygame.Rect(self.x, self.rect.y, self.rect.width, self.rect.height)

    def draw(self, screen):
        W = settings.WINDOW_WIDTH
        LEVEL_LENGTH = settings.get_level_length()
        screen_rect = pygame.Rect(W // 2, self.rect.y, self.rect.width, self.rect.height)
        if self.x < W // 2:
            screen_rect.x = self.x
        elif self.x > LEVEL_LENGTH - W // 2:
            screen_rect.x = self.x - (LEVEL_LENGTH - W)
        else:
            screen_rect.x = W // 2

        # Draw a simple character with head, body, eyes and animated limbs

        bx = int(screen_rect.x)
        by = int(screen_rect.y)
        bw = int(screen_rect.width)
        bh = int(screen_rect.height)

        # Alien body (rounded)
        body_color = (102, 255, 153)  # bright alien green
        belly_color = (200, 255, 220)
        body_rect = pygame.Rect(bx, by + bh * 0.3, bw, int(bh * 0.65))
        pygame.draw.ellipse(screen, body_color, body_rect)
        # Belly
        belly_rect = pygame.Rect(bx + bw*0.15, by + bh * 0.45, int(bw*0.7), int(bh*0.35))
        pygame.draw.ellipse(screen, belly_color, belly_rect)

        # Head (slightly oval)
        head_w = int(bw * 0.9)
        head_h = int(bh * 0.6)
        head_x = bx + bw // 2
        head_y = by + int(bh * 0.18)
        pygame.draw.ellipse(screen, body_color, (head_x - head_w//2, head_y - head_h//2, head_w, head_h))

        # Antennae
        t = pygame.time.get_ticks() / 300.0
        ant_bob = math.sin(t) * 4
        left_ant_start = (head_x - head_w//4, head_y - head_h//2 + 6)
        right_ant_start = (head_x + head_w//4, head_y - head_h//2 + 6)
        pygame.draw.line(screen, (180, 255, 200), left_ant_start, (left_ant_start[0] - 8, left_ant_start[1] - 24 + ant_bob), 3)
        pygame.draw.line(screen, (180, 255, 200), right_ant_start, (right_ant_start[0] + 8, right_ant_start[1] - 24 - ant_bob), 3)
        pygame.draw.circle(screen, (255, 100, 180), (left_ant_start[0] - 8, int(left_ant_start[1] - 24 + ant_bob)), 5)
        pygame.draw.circle(screen, (255, 100, 180), (right_ant_start[0] + 8, int(right_ant_start[1] - 24 - ant_bob)), 5)

        # Single big eye (cyclops)
        eye_radius = max(6, head_w // 6)
        eye_x = head_x + (6 if self.facing == 'right' else -6)
        eye_y = head_y
        pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), eye_radius)
        # pupil that looks slightly toward movement
        pupil_offset = 4 if self.facing == 'right' else -4
        pygame.draw.circle(screen, (20, 20, 40), (eye_x + pupil_offset, eye_y), max(3, eye_radius//2))

        # Mouth (small)
        mouth_y = head_y + head_h//4
        pygame.draw.arc(screen, (120, 40, 80), (head_x - head_w//6, mouth_y - 4, head_w//3, 12), math.pi/8, math.pi - math.pi/8, 2)

        # Tentacle legs (wavy)
        leg_y = by + bh
        leg_spread = bw // 3
        for i in range(-1, 2, 2):
            base_x = head_x + i * leg_spread//1
            points = []
            for s in range(6):
                px = base_x + int(math.sin(t + s * 0.6) * (6 if self.moving else 2)) * i
                py = leg_y + s * (bh * 0.08)
                points.append((px, int(py)))
            pygame.draw.lines(screen, (40, 40, 40), False, points, 4)

        # Small arms
        arm_y = by + int(bh * 0.5)
        pygame.draw.line(screen, (40, 40, 40), (head_x - bw//2 + 6, arm_y), (head_x - bw//2 - 8, arm_y + 8), 4)
        pygame.draw.line(screen, (40, 40, 40), (head_x + bw//2 - 6, arm_y), (head_x + bw//2 + 8, arm_y + 8), 4)

