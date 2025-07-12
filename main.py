import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, LEVEL_LENGTH, PLAYER_SPEED
from player import Player
from platforms import Platform
from obstacle import Obstacle
from goal import Goal
from hand_controller import HandController


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini Mario")
clock = pygame.time.Clock()

# Create objects
player = Player(100, 500)
platforms = [
    Platform(0, 580, 800, 20),
    Platform(300, 450, 100, 20),
    Platform(600, 450, 100, 20),
    Platform(900, 400, 100, 20),
    Platform(1200, 350, 100, 20),
    Platform(1500, 300, 100, 20),
    Platform(1800, 580, 200, 20)
]
obstacles = [
    Obstacle(700, 560, 40, 20),
    Obstacle(1300, 560, 40, 20),
    Obstacle(1600, 560, 40, 20)
]
goal = Goal(1950, 520, 30, 60)
hand_control = HandController()

# Game loop
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    hand_control.update()
    move_left, move_right, jump = hand_control.get_controls()

    if move_left:
        player.world_x = max(0, player.world_x - PLAYER_SPEED)
    if move_right:
        player.world_x = min(LEVEL_LENGTH - player.rect.width, player.world_x + PLAYER_SPEED)
    if jump:
        player.jump()

    # Check collisions and update position
    player.update(platforms)

    # Camera follows player but doesn't scroll beyond level bounds
    if player.world_x < SCREEN_WIDTH // 2:
        camera_offset = 0
    elif player.world_x > LEVEL_LENGTH - SCREEN_WIDTH // 2:
        camera_offset = LEVEL_LENGTH - SCREEN_WIDTH
    else:
        camera_offset = player.world_x - SCREEN_WIDTH // 2

    # Check collisions
    for obstacle in obstacles:
        if player.get_rect().colliderect(obstacle.rect):
            print("Game Over!")
            running = False

    if player.rect.y > SCREEN_HEIGHT:
        print("Game Over!")
        running = False

    if player.get_rect().colliderect(goal.rect):
        print("You Win!")
        running = False

    # Draw everything
    screen.fill((0, 0, 0))  # Black background
    player.draw(screen)
    for platform in platforms:
        platform.draw(screen, camera_offset)
    for obstacle in obstacles:
        obstacle.draw(screen, camera_offset)
    goal.draw(screen, camera_offset)
    pygame.display.flip()

pygame.quit()
sys.exit()