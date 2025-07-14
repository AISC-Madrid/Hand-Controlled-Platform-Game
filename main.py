#Note: remove commented lines of code to add an opponent

import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, LEVEL_LENGTH, PLAYER_SPEED
from player import Player
from platforms import Platform
#from obstacle import Obstacle
from goal import Goal
from hand_controller import HandController
import time

MAX_TIME_MS = 20000  # Time limit

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini Mario")
clock = pygame.time.Clock()

# Create font for text
font = pygame.font.SysFont(None, 36)  # You can change size and type

# Game States
START_SCREEN = 0
PLAYING = 1
WIN_SCREEN = 2
GAME_OVER_SCREEN = 3

game_state = START_SCREEN

def reset_game():
    global player, platforms, goal, start_ticks, game_state
    player = Player(100, 500)
    platforms = [
        Platform(0, 580, 800, 20),
        Platform(300, 450, 100, 20),
        Platform(600, 450, 100, 20),
        Platform(900, 400, 100, 20),
        Platform(1200, 350, 150, 20),
        Platform(1500, 300, 100, 20),
        Platform(1800, 580, 200, 20)
    ]
    goal = Goal(1950, 520, 30, 60)
    start_ticks = pygame.time.get_ticks()
    game_state = PLAYING # Set to PLAYING after reset

hand_control = HandController()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == START_SCREEN:
                if event.key == pygame.K_SPACE:
                    reset_game()
            elif game_state == WIN_SCREEN or game_state == GAME_OVER_SCREEN:
                if event.key == pygame.K_r: # Restart
                    reset_game()
                elif event.key == pygame.K_m: # Main Menu
                    game_state = START_SCREEN

    # Always update hand control for camera window to be active
    hand_control.update()
    # No need to get controls unless in PLAYING state for game logic
    # move_left, move_right, jump = hand_control.get_controls()


    if game_state == START_SCREEN:
        screen.fill((0, 0, 0))
        start_text = font.render("Press SPACE to Start", True, (255, 255, 255))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - start_text.get_height() // 2))

    elif game_state == PLAYING:
        clock.tick(FPS)

        # Remaining time calculation
        elapsed_ms = pygame.time.get_ticks() - start_ticks
        remaining_ms = max(0, MAX_TIME_MS - elapsed_ms)

        if remaining_ms == 0:
            print("Se acabó el tiempo. Game Over!")
            game_state = GAME_OVER_SCREEN

        # Get controls only when playing
        move_left, move_right, jump = hand_control.get_controls()

        if move_left:
            player.x = max(0, player.x - PLAYER_SPEED)
        if move_right:
            player.x = min(LEVEL_LENGTH - player.rect.width, player.x + PLAYER_SPEED)
        if jump:
            player.jump()

        # Check collisions and update position
        player.update(platforms)

        # Camera follows player but doesn't scroll beyond level bounds
        if player.x < SCREEN_WIDTH // 2:
            camera_offset = 0
        elif player.x > LEVEL_LENGTH - SCREEN_WIDTH // 2:
            camera_offset = LEVEL_LENGTH - SCREEN_WIDTH
        else:
            camera_offset = player.x - SCREEN_WIDTH // 2

        # Check collisions

        """"
        for obstacle in obstacles:
            if player.get_rect().colliderect(obstacle.rect):
                print("Game Over!")
                running = False
        """

        if player.rect.y > SCREEN_HEIGHT:
            print("Game Over!")
            game_state = GAME_OVER_SCREEN

        if player.get_rect().colliderect(goal.rect):
            print("You Win!")
            game_state = WIN_SCREEN

        # Draw everything
        screen.fill((0, 0, 0))  # Black background
        player.draw(screen)
        for platform in platforms:
            platform.draw(screen, camera_offset)
        """""
        for obstacle in obstacles:
            obstacle.update(platforms)
            obstacle.draw(screen, camera_offset)
        """
        goal.draw(screen, camera_offset)

        # To ms and s
        seconds = remaining_ms // 1000
        milliseconds = remaining_ms % 1000

        #Format text
        time_text = f"Tiempo: {seconds:02d},{milliseconds:03d}"

        text_surface = font.render(time_text, True, (255, 255, 255))
        screen.blit(text_surface, (20, 20))


    elif game_state == WIN_SCREEN:
        screen.fill((0, 0, 0))
        win_text = font.render("You Win!", True, (0, 255, 0))
        restart_text = font.render("Press 'R' to Restart or 'M' for Main Menu", True, (255, 255, 255))
        screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

    elif game_state == GAME_OVER_SCREEN:
        screen.fill((0, 0, 0))
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        restart_text = font.render("Press 'R' to Restart or 'M' for Main Menu", True, (255, 255, 255))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

    pygame.display.flip()

hand_control.release()
pygame.quit()
sys.exit()