# Default window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

def get_width_ratio():
    return WINDOW_WIDTH / 800

def get_height_ratio():
    return WINDOW_HEIGHT / 600

def get_player_speed():
    return 6 * get_width_ratio()

def get_jump_speed():
    return 10 * get_height_ratio()

def get_level_length():
    return 2000 * get_width_ratio()
