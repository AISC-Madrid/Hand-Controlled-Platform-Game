#This is ASIC Madrid's presentation game
#Authors: Lauren Gallego & Hugo Centeno

import pygame
import sys
from config import *
from player import Player
from platforms import Platform
from goal import Goal
from hand_controller import HandController
import settings
import os
import time

# Initialize game
pygame.init()

# Set screen to full size
screen = pygame.display.set_mode((0, 0))
settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT = screen.get_size()

# Import arcade font
font_path = os.path.join("fonts", "Arcade Classic.ttf")
font_title = pygame.font.Font(font_path, 64)
font_blinking = pygame.font.Font(font_path, 32)
font_time = pygame.font.Font(font_path, 26)

# Dimensions
W, H = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT

pygame.display.set_caption("Hand-Controlled Platform Game")
clock = pygame.time.Clock()

# Logo
try:
    start_image = pygame.image.load('images/AISC logo.png').convert_alpha()
    start_image = pygame.transform.scale(start_image, (100, 100))
except pygame.error as e:
    print(f"Error loading start image: {e}")
    start_image = None

game_state = START_SCREEN

def reset_game():
    """
    This function resets the game state and initializes the game objects.
    """
    global player, platforms, goal, start_ticks, game_state

    scale_x = settings.get_width_ratio()
    scale_y = settings.get_height_ratio()

    floor_height = 40 * scale_y
    floor_y = H - floor_height

    player = Player(100 * scale_x, floor_y - 500 * scale_y)

    platforms = [
        Platform(0, floor_y, 800 * scale_x, floor_height),
        Platform(300 * scale_x, 450 * scale_y, 100 * scale_x, 20 * scale_y),
        Platform(600 * scale_x, 450 * scale_y, 100 * scale_x, 20 * scale_y),
        Platform(900 * scale_x, 400 * scale_y, 100 * scale_x, 20 * scale_y),
        Platform(1200 * scale_x, 350 * scale_y, 150 * scale_x, 20 * scale_y),
        Platform(1500 * scale_x, 300 * scale_y, 100 * scale_x, 20 * scale_y),
        Platform(1850 * scale_x, floor_y, 200 * scale_x, floor_height)
    ]

    goal = Goal(1950 * scale_x, floor_y - 60 * scale_y, 30 * scale_x, 60 * scale_y)

    start_ticks = pygame.time.get_ticks()
    game_state = PLAYING

# Import Computer Vision system
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
            elif game_state in (WIN_SCREEN, GAME_OVER_SCREEN):
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_m:
                    game_state = START_SCREEN

    hand_control.update()

    if game_state == START_SCREEN:
        screen.fill(COLOR_BG)

        # Title
        title_text = font_title.render("MINI MARIO", True, COLOR_ACCENT)
        title_rect = title_text.get_rect(center=(W // 2, H // 5))
        screen.blit(title_text, title_rect)

        # Blinking Start Prompt
        if int(time.time() * 2) % 2 == 0:
            start_msg = font_blinking.render("PRESS SPACE TO START", True, COLOR_TEXT)
            screen.blit(start_msg, (W // 2 - start_msg.get_width() // 2, H // 2 + 50))

        # Optional logo
        if start_image:
            image_rect = start_image.get_rect(center=(W // 2, H - 150))
            screen.blit(start_image, image_rect)


    elif game_state == PLAYING:
        clock.tick(FPS)
        elapsed_ms = pygame.time.get_ticks() - start_ticks
        remaining_ms = max(0, MAX_TIME_MS - elapsed_ms)
        if remaining_ms == 0:
            game_state = GAME_OVER_SCREEN

        move_left, move_right, jump = hand_control.get_controls()

        if move_left:
            player.x = max(0, player.x - settings.get_player_speed())
        if move_right:
            player.x = min(settings.get_level_length() - player.rect.width, player.x + settings.get_player_speed())
        if jump:
            player.jump()

        player.update(platforms)

        if player.x < W // 2:
            camera_offset = 0
        elif player.x > settings.get_level_length() - W // 2:
            camera_offset = settings.get_level_length() - W
        else:
            camera_offset = player.x - W // 2

        if player.rect.y > H:
            game_state = GAME_OVER_SCREEN

        if player.get_rect().colliderect(goal.rect):
            game_state = WIN_SCREEN

        screen.fill((0, 0, 0))
        if start_image:
            image_rect = start_image.get_rect(center=(W - W // 10, H // 9))
            screen.blit(start_image, image_rect)
        player.draw(screen)
        for platform in platforms:
            platform.draw(screen, camera_offset)

        goal.draw(screen, camera_offset)
        seconds = remaining_ms // 1000
        milliseconds = remaining_ms % 1000
        time_text = f"Time: {seconds:02d},{milliseconds:03d}"
        text_surface = font_time.render(time_text, True, (255, 255, 255))
        screen.blit(text_surface, (20, 20))


    elif game_state == WIN_SCREEN:

        screen.fill(COLOR_BG)

        # Title
        msg_text = font_title.render("YOU WIN!", True, (0, 255, 0))
        msg_rect = msg_text.get_rect(center=(W // 2, H // 3))
        screen.blit(msg_text, msg_rect)

        # Restart Prompt
        if int(time.time() * 2) % 2 == 0:
            prompt = font_blinking.render("R - RESTART      M - MENU", True, COLOR_TEXT)
            screen.blit(prompt, (W // 2 - prompt.get_width() // 2, H // 2 + 50))

        if start_image:
            image_rect = start_image.get_rect(center=(W // 2, H - 120))
            screen.blit(start_image, image_rect)

    elif game_state == GAME_OVER_SCREEN:

        screen.fill(COLOR_BG)

        # Title
        msg_text = font_title.render("GAME OVER", True, (255, 0, 0))
        msg_rect = msg_text.get_rect(center=(W // 2, H // 3))
        screen.blit(msg_text, msg_rect)

        # Restart Prompt
        if int(time.time() * 2) % 2 == 0:
            prompt = font_blinking.render("R - RESTART      M - MENU", True, COLOR_TEXT)
            screen.blit(prompt, (W // 2 - prompt.get_width() // 2, H // 2 + 50))

        if start_image:
            image_rect = start_image.get_rect(center=(W // 2, H - 120))

            screen.blit(start_image, image_rect)

    pygame.display.flip()

hand_control.release()
pygame.quit()
sys.exit()
