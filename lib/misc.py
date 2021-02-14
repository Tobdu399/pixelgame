# Import pygame library without the version and welcome message
import contextlib
with contextlib.redirect_stdout(None):
    import pygame

import pathlib

path = str(pathlib.Path(__file__).resolve().parent)

pygame.init()

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Pixel Game")
clock   = pygame.time.Clock()

WIDTH, HEIGHT = pygame.display.get_surface().get_size()
FPS           = 120
GAME_RUNNING  = True
MENU_OPEN     = False
DEBUG_SCREEN  = False

# Color and its definition
color_list = {
    "dark green": "Enemy's danger zone",
    "green": "Enemy can shoot at the player",
    "red": "Enemy can't shoot at the player",
    "purple": "Player's sight",
    "yellow": "Character's center"
}

# Menu option and it's color
menu_options         = {"Close": "white", "Restart": "white", "Quit": "white"}
menu_highlight_color = "green"

# Images
background_img = pygame.image.load(f"{path}/pictures/display/grass.png").convert()

gunmen        = []
gunman_images = {
    "idle": (pygame.image.load(f"{path}/pictures/gunman/gunman.png"), (127, 76)),
}

player_images = {
    "idle":  (pygame.image.load(f"{path}/pictures/player/player_idle.png"), (127, 76)),

    "shoot": [
        (pygame.image.load(f"{path}/pictures/player/player_shoot_0.png"), (125, 75)),
        (pygame.image.load(f"{path}/pictures/player/player_shoot_1.png"), (125, 75)),
        (pygame.image.load(f"{path}/pictures/player/player_shoot_2.png"), (125, 75)),
    ],

    "reload": [
        (pygame.image.load(f"{path}/pictures/player/player_reload_0.png"), (125, 75)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_1.png"), (125, 76)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_2.png"), (125, 77)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_3.png"), (125, 78)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_4.png"), (125, 80)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_5.png"), (125, 82)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_6.png"), (125, 83)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_7.png"), (125, 85)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_8.png"), (125, 85)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_9.png"), (125, 84)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_10.png"), (125, 82)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_11.png"), (125, 80)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_12.png"), (125, 78)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_13.png"), (125, 76)),
        (pygame.image.load(f"{path}/pictures/player/player_reload_14.png"), (125, 76)),
    ]
}

# Sound Effects
pistol_shoot  = pygame.mixer.Sound(f"{path}/sfx/pistol_shoot.mp3")
pistol_reload = pygame.mixer.Sound(f"{path}/sfx/pistol_reload.mp3")
button_hover  = pygame.mixer.Sound(f"{path}/sfx/button_hover.mp3")
button_click  = pygame.mixer.Sound(f"{path}/sfx/button_click.mp3")

pygame.mixer.music.load(f"{path}/music/music.mp3")

# Set sounds' default volume
pygame.mixer.music.set_volume(0.06)

pistol_shoot.set_volume(0.6)
pistol_reload.set_volume(0.2)
button_hover.set_volume(0.2)
button_click.set_volume(0.2)
