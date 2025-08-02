import pygame
import settings
from config import GRAVITY

class Player:
    def __init__(self, x, y, width=30, height=60):
        scale_x = settings.get_width_ratio()
        scale_y = settings.get_height_ratio()

        self.rect = pygame.Rect(x, y, width * scale_x, height * scale_y)
        self.x = x
        self.vel_y = 0
        self.on_ground = False

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

        pygame.draw.rect(screen, (235, 23, 142), screen_rect)
