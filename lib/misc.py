# Import pygame library without the version and welcome message
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

import pathlib

path = str(pathlib.Path(__file__).resolve().parent)

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, buffer=2**12)

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Pixel Game")
clock = pygame.time.Clock()

WIDTH, HEIGHT    = pygame.display.get_surface().get_size()
FPS              = 120

GAME_OPEN        = True
START_MENU_OPEN  = True
GAME_RUNNING     = False
MENU_OPEN        = False
DEBUG_SCREEN     = False
FADE_IN          = False

ROUND            = 0
GUNMEN_AMOUNT    = 0
SCORE            = 0
SCORE_MULTIPLIER = 1
FADE_ALPHA       = 0

# Color and its definition
color_list = {
    "dark green": "Enemy's danger zone",
    "green": "Enemy can shoot at the player",
    "red": "Enemy can't shoot at the player",
    "purple": "Player's sight",
    "yellow": "Character's center"
}

# Menu option and it's color
menu_options         = {"Close": "white", "Restart Game": "white", "Save And Quit": "white"}
start_menu_options   = {"Start New Game": "white", "Load Previous Game": "white", "Quit": "white"}
menu_highlight_color = "green"

# Images
# NOTE: Converting images to alpha increases the game performance significantly
icon = pygame.image.load(f"{path}/pictures/display/icon.png").convert_alpha(display)
pygame.display.set_icon(icon)

background_img = pygame.image.load(f"{path}/pictures/display/grass.png").convert_alpha(display)
background_img_rect = background_img.get_rect()

start_menu_background_img = pygame.image.load(f"{path}/pictures/display/start_menu.png").convert_alpha(display)
start_menu_background_img = pygame.transform.scale(start_menu_background_img, (WIDTH, HEIGHT))

gunmen = []
gunman_images = {
    "idle": (pygame.image.load(f"{path}/pictures/gunman/gunman_idle.png").convert_alpha(display), (140, 75)),

    "shoot": [
        (pygame.image.load(f"{path}/pictures/gunman/gunman_shoot_0.png").convert_alpha(display), (140, 75)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_shoot_1.png").convert_alpha(display), (140, 75)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_shoot_2.png").convert_alpha(display), (140, 75)),
    ],

    "reload": [
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_0.png").convert_alpha(display), (140, 75)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_1.png").convert_alpha(display), (140, 76)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_2.png").convert_alpha(display), (140, 76)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_3.png").convert_alpha(display), (140, 77)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_4.png").convert_alpha(display), (140, 77)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_5.png").convert_alpha(display), (140, 78)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_6.png").convert_alpha(display), (140, 78)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_7.png").convert_alpha(display), (140, 78)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_8.png").convert_alpha(display), (140, 78)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_9.png").convert_alpha(display), (140, 78)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_10.png").convert_alpha(display), (140, 78)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_11.png").convert_alpha(display), (140, 78)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_12.png").convert_alpha(display), (140, 79)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_13.png").convert_alpha(display), (140, 79)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_14.png").convert_alpha(display), (140, 79)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_15.png").convert_alpha(display), (140, 78)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_16.png").convert_alpha(display), (140, 77)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_17.png").convert_alpha(display), (140, 76)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_18.png").convert_alpha(display), (140, 75)),
        (pygame.image.load(f"{path}/pictures/gunman/gunman_reload_19.png").convert_alpha(display), (140, 75)),
    ]
}

player_images = {
    "idle": (pygame.image.load(f"{path}/pictures/player/player_idle.png").convert_alpha(display), (127, 76)),

    "shoot": [
        (pygame.image.load(f"{path}/pictures/player/player_shoot_0.png").convert_alpha(display), (125, 75)),
        (pygame.image.load(f"{path}/pictures/player/player_shoot_1.png").convert_alpha(display), (125, 75)),
        (pygame.image.load(f"{path}/pictures/player/player_shoot_2.png").convert_alpha(display), (125, 75)),
    ],

    "reload": [
        (pygame.image.load(f"{path}/pictures/player/player_reload_0.png").convert_alpha(display), (125, 75)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_1.png").convert_alpha(display), (125, 76)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_2.png").convert_alpha(display), (125, 77)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_3.png").convert_alpha(display), (125, 78)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_4.png").convert_alpha(display), (125, 80)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_5.png").convert_alpha(display), (125, 82)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_6.png").convert_alpha(display), (125, 83)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_7.png").convert_alpha(display), (125, 85)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_8.png").convert_alpha(display), (125, 85)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_9.png").convert_alpha(display), (125, 84)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_10.png").convert_alpha(display), (125, 82)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_11.png").convert_alpha(display), (125, 80)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_12.png").convert_alpha(display), (125, 78)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_13.png").convert_alpha(display), (125, 76)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_14.png").convert_alpha(display), (125, 76)),
    ]
}

# Sound Effects
pistol_shoot  = pygame.mixer.Sound(f"{path}/sfx/pistol_shoot.wav")
pistol_reload = pygame.mixer.Sound(f"{path}/sfx/pistol_reload.wav")
rifle_shoot   = pygame.mixer.Sound(f"{path}/sfx/rifle_shoot.wav")
rifle_reload  = pygame.mixer.Sound(f"{path}/sfx/rifle_reload.wav")
pistol_empty  = pygame.mixer.Sound(f"{path}/sfx/pistol_empty.wav")

button_hover = pygame.mixer.Sound(f"{path}/sfx/button_hover.wav")
button_click = pygame.mixer.Sound(f"{path}/sfx/button_click.wav")

# Set sounds' default volume
pistol_shoot.set_volume(0.6)
pistol_reload.set_volume(0.2)
rifle_shoot.set_volume(0.8)
rifle_reload.set_volume(0.05)
pistol_empty.set_volume(0.1)

button_hover.set_volume(0.05)
button_click.set_volume(0.2)
