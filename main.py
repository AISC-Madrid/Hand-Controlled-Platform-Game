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
import csv
from registry.registry import UserRegistry

# Initialize game
pygame.init()

# System cursors (create once)
try:
    cursor_arrow = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
    cursor_ibeam = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_IBEAM)
    cursor_hand = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)
except Exception:
    cursor_arrow = cursor_ibeam = cursor_hand = None
current_cursor = None

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

# Landing form state
landing_name = ""
landing_email = ""
landing_active_field = None  # None, 'name', or 'email'
landing_error = ""

# User registry (handles CSV, duplication checks and validation)
user_registry = UserRegistry()

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
    # Precompute landing form rectangles when on start screen
    if game_state == START_SCREEN:
        form_width = int(W * 0.6)
        form_x = (W - form_width) // 2
        form_y = H // 2 - 80
        name_rect = pygame.Rect(form_x, form_y, form_width, 40)
        email_rect = pygame.Rect(form_x, form_y + 60, form_width, 40)
        start_btn_rect = pygame.Rect(form_x + form_width // 2 - 60, form_y + 130, 120, 40)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse clicks: select field or press start
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == START_SCREEN:
                mx, my = event.pos
                if name_rect.collidepoint(mx, my):
                    landing_active_field = 'name'
                elif email_rect.collidepoint(mx, my):
                    landing_active_field = 'email'
                elif start_btn_rect.collidepoint(mx, my):
                    success, msg = user_registry.add_user(landing_name.strip(), landing_email.strip())
                    landing_error = '' if success else msg
                    if success:
                        reset_game()

        # Keyboard input
        if event.type == pygame.KEYDOWN:
            if game_state == START_SCREEN:
                if landing_active_field:
                    if event.key == pygame.K_BACKSPACE:
                        if landing_active_field == 'name':
                            landing_name = landing_name[:-1]
                        else:
                            landing_email = landing_email[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # If on name, move to email; if on email, submit
                        if landing_active_field == 'name':
                            landing_active_field = 'email'
                        else:
                            success, msg = user_registry.add_user(landing_name.strip(), landing_email.strip())
                            landing_error = '' if success else msg
                            if success:
                                reset_game()
                    else:
                        ch = event.unicode
                        if ch and len(ch) == 1:
                            if landing_active_field == 'name':
                                landing_name += ch
                            else:
                                landing_email += ch
                else:
                    # if no field selected, allow selecting with Enter to focus name
                    if event.key == pygame.K_RETURN:
                        landing_active_field = 'name'
            elif game_state in (WIN_SCREEN, GAME_OVER_SCREEN):
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_m:
                    game_state = START_SCREEN

    hand_control.update()

    # Update cursor based on hover over form elements (start screen)
    if game_state == START_SCREEN:
        try:
            mx, my = pygame.mouse.get_pos()
            desired = cursor_arrow
            if name_rect.collidepoint(mx, my) or email_rect.collidepoint(mx, my):
                desired = cursor_ibeam
            elif start_btn_rect.collidepoint(mx, my):
                desired = cursor_hand

            if desired is not None and desired is not current_cursor:
                pygame.mouse.set_cursor(desired)
                current_cursor = desired
        except Exception:
            pass

    if game_state == START_SCREEN:
        screen.fill(COLOR_BG)

        # Title
        title_text = font_title.render("MINI MARIO", True, COLOR_ACCENT)
        title_rect = title_text.get_rect(center=(W // 2, H // 5))
        screen.blit(title_text, title_rect)

        # Landing form
        # Draw name field
        pygame.draw.rect(screen, (255, 255, 255) if landing_active_field == 'name' else (200, 200, 200), name_rect, 0)
        name_label = font_time.render('Name:', True, (32, 204, 241))
        screen.blit(name_label, (name_rect.x + 8, name_rect.y - 24))
        name_text_surf = font_time.render(landing_name or '', True, (0, 0, 0))
        screen.blit(name_text_surf, (name_rect.x + 8, name_rect.y + 6))

        # Draw email field
        pygame.draw.rect(screen, (255, 255, 255) if landing_active_field == 'email' else (200, 200, 200), email_rect, 0)
        email_label = font_time.render('Email:', True, (32, 204, 241))
        screen.blit(email_label, (email_rect.x + 8, email_rect.y - 24))
        email_text_surf = font_time.render(landing_email or '', True, (0, 0, 0))
        screen.blit(email_text_surf, (email_rect.x + 8, email_rect.y + 6))

        # Draw start button
        pygame.draw.rect(screen, COLOR_ACCENT, start_btn_rect)
        btn_text = font_blinking.render('START', True, COLOR_TEXT)
        btn_rect = btn_text.get_rect(center=start_btn_rect.center)
        screen.blit(btn_text, btn_rect)

        # Show validation / duplicate error (if any)
        if landing_error:
            err_surf = font_time.render(landing_error, True, (255, 50, 50))
            screen.blit(err_surf, (form_x, start_btn_rect.y + 50))

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
