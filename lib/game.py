import math
import random
import pathlib

# Import pygame library without the version and welcome message
import contextlib
with contextlib.redirect_stdout(None):
    import pygame

path = str(pathlib.Path(__file__).resolve().parent)
pygame.init()

pygame.display.set_caption("Pixel Game")
display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, pygame.FULLSCREEN)
clock   = pygame.time.Clock()

WIDTH, HEIGHT = pygame.display.get_surface().get_size()
FPS           = 120
GAME_RUNNING  = True
MENU_OPEN     = False
DEBUG_SCREEN  = False

# Color and its definition
color_list = {
    "light blue": "Enemy's danger zone",
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
pygame.mixer.music.set_volume(0.03)

pistol_shoot.set_volume(0.6)
pistol_reload.set_volume(0.2)
button_hover.set_volume(0.1)
button_click.set_volume(0.2)


class Player:
    def __init__(self, x, y, images):
        self.x = x
        self.y = y
        self.steps  = 0
        self.images = images
        self.angle  = 0

        self.current_image = self.images["idle"]
        self.counter       = 0
        self.frame         = 0

        self.shooting      = False
        self.reloading     = False

    def show(self):
        # Calculate the self.angle in which the player is positioned
        mouse_x, mouse_y = pygame.mouse.get_pos()

        w = mouse_x - self.x
        h = mouse_y - self.y

        # If the player is not in the same x position as the mouse, calculate the new angle for the player.
        # But if the player is in the same x position as the mouse, then w would be 0 and then the angle calculation
        # wouldn't work because dividing by 0 is not possible
        if not MENU_OPEN:
            if w != 0:
                self.angle = math.degrees(math.atan(h / w))

            if w < 0:
                self.angle += 180

        # Animation
        if self.shooting or self.reloading and not MENU_OPEN:
            if self.counter % 5 == 0 and self.counter != 0:
                self.frame += 1
            self.counter += 1

        self.shooting = self.animate(self.shooting, self.images["shoot"], self.images["idle"])
        self.reloading = self.animate(self.reloading, self.images["reload"], self.images["idle"])

        # Scale and rotate the player image
        current_image = pygame.transform.scale(self.current_image[0], self.current_image[1])
        rotated_img, rotated_img_rect = rotate_image(current_image, self.angle, self.x, self.y)

        # Display the player
        display.blit(rotated_img, rotated_img_rect)

    def animate(self, busy, anim_images, idle_image):
        if busy:
            if self.frame >= len(anim_images):
                self.frame = self.counter = 0
                self.current_image = idle_image
                return False
            else:
                self.current_image = anim_images[self.frame]
                return True

    def move(self, x_dir, y_dir):
        self.x += x_dir
        self.y += y_dir


class Gunman:
    def __init__(self, x, y, danger_zone, image):
        self.x = x
        self.y = y
        self.danger_zone     = danger_zone
        self.angle           = 0
        self.image           = image["idle"]
        self.health          = 100
        self.is_alive        = True
        self.player_distance = 0

    def show(self):
        # Calculate the self.angle in which the gunman is positioned using argus tangent
        w = player.x - self.x   # leg's width
        h = player.y - self.y   # leg's height

        self.player_distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)  # distance
        # TODO: Give some kind of signal when the gunman is able to shoot the player

        # TODO: If the player is inside the enemy's danger zone, try to shoot the player
        #  if self.player_distance < self.danger_zone

        if w != 0 and not MENU_OPEN:
            self.angle = math.degrees(math.atan(h / w))
            if w < 0:
                self.angle += 180

        # Remove a really quick rotation when the player's x position is the same as the gunman's.
        # w won't be exactly 0 so check if it is close to 0
        elif w < 0.1 < w and self.player_distance < self.danger_zone:
            if player.x < self.x:
                self.angle = -90
            else:
                self.angle = 90

        # Scale and rotate the gunman image
        current_image = pygame.transform.scale(self.image[0], self.image[1])
        rotated_img, rotated_img_rect = rotate_image(current_image, self.angle, self.x, self.y)

        # Display the gunman if it is alive
        if self.health > 0:
            display.blit(rotated_img, rotated_img_rect.topleft)

            # Display the health bar if the gunman doesn't have full health
            if self.health != 100:
                health_bar_x = rotated_img_rect.x+(rotated_img_rect.width/2)-50
                health_bar_y = rotated_img_rect.y-15
                health_bar_height = 7

                pygame.draw.rect(display, "red", (health_bar_x, health_bar_y, 100, health_bar_height), border_radius=2)
                pygame.draw.rect(display, "green", (health_bar_x, health_bar_y, self.health, health_bar_height), border_radius=2)
        else:
            self.is_alive = False

    def hit(self):
        current_image = pygame.transform.scale(self.image[0], self.image[1])
        gunman_rect = rotate_image(current_image, self.angle, self.x, self.y)[1]

        # if self.player_distance < self.danger_zone and gunman_rect.collidepoint(pygame.mouse.get_pos()):
        if gunman_rect.collidepoint(pygame.mouse.get_pos()):
            self.health -= 10


def rotate_image(image, angle, x, y):
    # By default pygame.transform.rotate rotates the image to
    # left so to turn it right instead the self.angle must be multiplied by -1
    angle = angle * -1

    # TODO: For some reason the image is tuple (problem in Gunman)! Try to fix it
    if isinstance(image, list):
        rotated_image = pygame.transform.rotate(image[0], angle)
        new_rect = rotated_image.get_rect(center=image[0].get_rect(center=(x, y)).center)
    else:
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)

    return rotated_image, new_rect


def debug_screen():
    # Debug screen (press F3 to show)
    if DEBUG_SCREEN:
        font = pygame.font.Font(path + "/fonts/font.ttf", 15)
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for gun_man in gunmen:
            if gun_man.is_alive:
                distance = math.sqrt((player.x - gun_man.x) ** 2 + (player.y - gun_man.y) ** 2)

                if distance > gun_man.danger_zone:
                    color = "red"
                else:
                    color = "green"

                pygame.draw.circle(display, "light blue", (gun_man.x, gun_man.y), gun_man.danger_zone, 3)
                pygame.draw.line(display, color, (gun_man.x, gun_man.y), (player.x, player.y), 3)
                pygame.draw.circle(display, "yellow", (gun_man.x, gun_man.y), 5)

        pygame.draw.line(display, "purple", (player.x, player.y), (mouse_x, mouse_y), 3)
        pygame.draw.circle(display, "yellow", (player.x, player.y), 5)

        # Color info overlay's background
        info_bg = pygame.Surface((370, (len(color_list.keys()) * 20) + 50), pygame.SRCALPHA)
        info_bg.fill((0, 0, 0, 128))
        display.blit(info_bg, (0, 0))

        # Title
        title = font.render("DEBUG SCREEN", True, pygame.Color("white"))
        display.blit(title, (10, 10))

        # FPS
        fps = font.render(f"{str(int(clock.get_fps()))} FPS", True, pygame.Color("yellow"))
        display.blit(fps, (295, 10))

        # Show color and its definition
        y_pos = 40
        for color in color_list:
            pygame.draw.rect(display, color, (10, y_pos, 15, 15))
            text = font.render(color_list[color], True, pygame.Color(color))
            display.blit(text, (30, y_pos - 1))
            y_pos += 20


def menu():
    if MENU_OPEN:
        # Using pygame.draw.rect for the menu borders because pygame.Surface doesn't have the border radius setting.
        # Then positioning the pygame.Surface slightly inside the borders so that the corners wouldn't show

        # Menu border
        x, y                 = int(WIDTH / 4), int(HEIGHT / 4)
        width, height        = int(WIDTH / 2), int(HEIGHT / 2)
        border_width, radius = 10, 10

        pygame.draw.rect(display, "white", (x, y, width, height), border_width, border_radius=radius)

        # Menu background
        info_bg = pygame.Surface((int(WIDTH / 2) - 10, int(HEIGHT / 2) - 10), pygame.SRCALPHA)
        info_bg.fill((0, 0, 0, 200))
        display.blit(info_bg, (int(WIDTH / 4) + 5, int(HEIGHT / 4) + 5))

        # Title
        title_font = pygame.font.Font(path + "/fonts/pixel_font.ttf", int(HEIGHT/20))
        title = title_font.render("MENU", True, pygame.Color("white"))
        title_rect = title.get_rect(center=(int(WIDTH / 2), int(HEIGHT / 4) + 60))
        display.blit(title, title_rect)


def show_menu_options(event):
    global MENU_OPEN

    if MENU_OPEN:
        y_pos = 0
        space_between_options = int(HEIGHT/20)

        for option in menu_options.keys():
            option_font = pygame.font.Font(path + "/fonts/pixel_font.ttf", int(HEIGHT/30))
            option_text = option_font.render(option, True, pygame.Color(menu_options[option]))

            x = int(WIDTH / 2)
            y = int(HEIGHT / 2) - len(menu_options.keys()) * (space_between_options / len(menu_options.keys())) + y_pos

            option_text_rect = option_text.get_rect(center=(x, y))

            display.blit(option_text, option_text_rect)
            y_pos += space_between_options

            if option_text_rect.collidepoint(pygame.mouse.get_pos()):
                # Highlight Quit option in red
                if option == "Quit":
                    highlight_color = "red"

                    # Simple way of checkin whether to play the button hover sound or not
                    if menu_options[option] != "red":
                        button_hover.play()
                else:
                    highlight_color = menu_highlight_color

                    # Simple way of checkin whether to play the button hover sound or not
                    if menu_options[option] != menu_highlight_color:
                        button_hover.play()

                menu_options[option] = highlight_color
            else:
                menu_options[option] = "white"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if option_text_rect.collidepoint(pygame.mouse.get_pos()):
                    button_click.play()

                    # Decide what happens when one of the menu options is clicked
                    if option == "Close":
                        MENU_OPEN = False
                    elif option == "Restart":
                        game_setup()
                    elif option == "Quit":
                        exit_game()


def spawn_gunmen():
    gunmen.clear()

    # Create gunman
    for _ in range(5):
        gm_x_pos = random.randint(100, WIDTH - 100)
        gm_y_pos = random.randint(100, HEIGHT - 100)
        gm_danger_zone = 400

        gunmen.append(Gunman(gm_x_pos, gm_y_pos, gm_danger_zone, gunman_images))


def exit_game():
    global GAME_RUNNING

    GAME_RUNNING = False
    pygame.mixer.music.stop()

    pygame.quit()
    exit()


def game_setup():
    global player, MENU_OPEN

    # Create new player
    player = Player(int(WIDTH/2), int(HEIGHT/2), player_images)

    # Spawn gunmen
    spawn_gunmen()

    # Close the menu if it is open when starting the game
    if MENU_OPEN:
        MENU_OPEN = False

    # If the mouse's x position is set to the same position as the player's, the player won't turn
    # towards the cursor until it moves
    pygame.mouse.set_pos((int(WIDTH/2)+1, int(HEIGHT/2)-100))


def draw_background():
    background_img_rect = background_img.get_rect()

    y_pos = 0

    for _ in range(math.ceil(WIDTH/background_img_rect.width)):
        x_pos = 0
        for _ in range(math.ceil(HEIGHT/background_img_rect.height)):
            display.blit(background_img, (x_pos, y_pos))
            x_pos += background_img_rect.width

        y_pos += background_img_rect.height


def main():
    global MENU_OPEN, DEBUG_SCREEN

    game_setup()
    pygame.mixer.music.play(-1, 0.0)

    while GAME_RUNNING:
        # Game background
        display.fill("dark green")
        draw_background()

        # Display the gunmen
        for gunman in gunmen:
            gunman.show()

        # Show player sight
        if MENU_OPEN:
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)
            pygame.draw.circle(display, "red", (pygame.mouse.get_pos()), 5)

        # Display the player
        player.show()

        # Debug screen (press F3 to show)
        debug_screen()

        # Menu
        menu()

        # Player movement
        if not MENU_OPEN:
            keys = pygame.key.get_pressed()

            # If the user holds shift key, the player will run faster
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                movement_speed = 1
            else:
                movement_speed = 0.5

            # Use WASD for movement
            if keys[pygame.K_w]:
                player.move(0, -movement_speed)
            if keys[pygame.K_a]:
                player.move(-movement_speed, 0)
            if keys[pygame.K_s]:
                player.move(0, movement_speed)
            if keys[pygame.K_d]:
                player.move(movement_speed, 0)

        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            exit_game()

        # Shoot
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not MENU_OPEN:
            if not player.reloading and not player.shooting:
                player.shooting = True
                pistol_shoot.play()

            # Check if the player hit the gunman
            if player.shooting:
                for gunman in gunmen:
                    gunman.hit()

        if event.type == pygame.KEYDOWN:
            # Reload
            if event.key == pygame.K_r and not player.reloading and not MENU_OPEN:
                if not player.shooting:
                    player.reloading = True
                    pistol_reload.play()

            # Open pause menu
            if event.key == pygame.K_ESCAPE:
                MENU_OPEN = not MENU_OPEN

            # Toggle debug screen
            if event.key == pygame.K_F3:
                DEBUG_SCREEN = not DEBUG_SCREEN

        # Show menu options
        if MENU_OPEN:
            show_menu_options(event)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    exit()
