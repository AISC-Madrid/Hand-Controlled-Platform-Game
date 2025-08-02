import pygame
from config import JUMP_SPEED, GRAVITY
from platforms import Platform
import random

class Obstacle:
    def __init__(self, x, y, width, height, speed, platform: Platform):
        self.rect = pygame.Rect(x, y, width, height)
        self.platform = platform
        self.bounds = (platform.rect.x, platform.rect.x + platform.rect.width - width)
        self.x = x
        self.vel_y = 0
        self.on_ground = False
        self.speed = speed
        self.direction = random.choice((-1, 1))
        self.jump_timer = 0

    def draw(self, screen, camera_offset):
        draw_rect = pygame.Rect(self.rect.x - camera_offset, self.rect.y, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, (255, 0, 0), draw_rect)

    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_SPEED
            self.on_ground = False

    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

    def move(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x < self.bounds[0] or self.rect.x > self.bounds[1]:
            self.direction *= -1

        self.jump_timer += 1
        if self.jump_timer > 30 and random.random() < 0.03:
            self.jump()
            self.jump_timer = 0

    def check_collision(self, platforms):
        if self.vel_y > 0:  # Only check if falling
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    return

    def update(self, platforms):
        self.move()
        self.apply_gravity()
        self.check_collision(platforms)



