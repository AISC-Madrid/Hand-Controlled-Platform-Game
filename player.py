import pygame
from config import GRAVITY, PLAYER_SPEED, JUMP_SPEED, SCREEN_WIDTH

class Player:
    def __init__(self, x, y, width=40, height=60):
        self.rect = pygame.Rect(x, y, width, height)
        self.world_x = x
        self.vel_y = 0
        self.on_ground = False


    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_SPEED
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
        return pygame.Rect(self.world_x, self.rect.y, self.rect.width, self.rect.height)

    def draw(self, screen):
        screen_rect = pygame.Rect(SCREEN_WIDTH // 2, self.rect.y, self.rect.width, self.rect.height)
        if self.world_x < SCREEN_WIDTH // 2:
            screen_rect.x = self.world_x
        elif self.world_x > 2000 - SCREEN_WIDTH // 2:
            screen_rect.x = self.world_x - (2000 - SCREEN_WIDTH)
        pygame.draw.rect(screen, (0, 0, 255), screen_rect)