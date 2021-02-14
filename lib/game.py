import math
import random
from lib import misc
from lib import slider

# Sliders
sfx_volume = slider.Slider(int(misc.WIDTH/4) + 50, int(misc.HEIGHT / 2) + int(misc.HEIGHT / 4) - 75, 200, "grey", "white", misc.pistol_shoot.get_volume(), 1)
music_volume = slider.Slider(int(misc.WIDTH / 4) + 50, int(misc.HEIGHT / 2) + int(misc.HEIGHT / 4) - 50, 200, "grey", "white", misc.pygame.mixer.music.get_volume(), 0.2)

slider.sliders.append(sfx_volume)
slider.sliders.append(music_volume)


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
        mouse_x, mouse_y = misc.pygame.mouse.get_pos()

        w = mouse_x - self.x
        h = mouse_y - self.y

        # If the player is not in the same x position as the mouse, calculate the new angle for the player.
        # But if the player is in the same x position as the mouse, then w would be 0 and then the angle calculation
        # wouldn't work because dividing by 0 is not possible
        if not misc.MENU_OPEN:
            if w != 0:
                self.angle = math.degrees(math.atan(h / w))

            if w < 0:
                self.angle += 180

        # Animation
        if self.shooting or self.reloading and not misc.MENU_OPEN:
            if self.counter % 5 == 0 and self.counter != 0:
                self.frame += 1
            self.counter += 1

        self.shooting = self.animate(self.shooting, self.images["shoot"], self.images["idle"])
        self.reloading = self.animate(self.reloading, self.images["reload"], self.images["idle"])

        # Scale and rotate the player image
        current_image = misc.pygame.transform.scale(self.current_image[0], self.current_image[1])
        rotated_img, rotated_img_rect = rotate_image(current_image, self.angle, self.x, self.y)

        # misc.display the player
        misc.display.blit(rotated_img, rotated_img_rect)

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
        w = player.x - self.x   # leg's misc.WIDTH
        h = player.y - self.y   # leg's misc.HEIGHT

        self.player_distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)  # distance
        # TODO: Give some kind of signal when the gunman is able to shoot the player

        # TODO: If the player is inside the enemy's danger zone, try to shoot the player
        #  if self.player_distance < self.danger_zone

        if w != 0 and not misc.MENU_OPEN:
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
        current_image = misc.pygame.transform.scale(self.image[0], self.image[1])
        rotated_img, rotated_img_rect = rotate_image(current_image, self.angle, self.x, self.y)

        # misc.display the gunman if it is alive
        if self.health > 0:
            misc.display.blit(rotated_img, rotated_img_rect.topleft)

            # misc.display the health bar if the gunman doesn't have full health
            if self.health != 100:
                health_bar_x = rotated_img_rect.x+(rotated_img_rect.width/2)-50
                health_bar_y = rotated_img_rect.y-15
                health_bar_height = 7

                misc.pygame.draw.rect(misc.display, "red", (health_bar_x, health_bar_y, 100, health_bar_height), border_radius=2)
                misc.pygame.draw.rect(misc.display, "green", (health_bar_x, health_bar_y, self.health, health_bar_height), border_radius=2)
        else:
            self.is_alive = False

    def hit(self):
        current_image = misc.pygame.transform.scale(self.image[0], self.image[1])
        gunman_rect = rotate_image(current_image, self.angle, self.x, self.y)[1]

        if gunman_rect.collidepoint(misc.pygame.mouse.get_pos()):
            self.health -= 10


def rotate_image(image, angle, x, y):
    # By default misc.pygame.transform.rotate rotates the image to
    # left so to turn it right instead the self.angle must be multiplied by -1
    angle = angle * -1

    # TODO: For some reason the image is tuple (problem in Gunman)! Try to fix it
    if isinstance(image, list):
        rotated_image = misc.pygame.transform.rotate(image[0], angle)
        new_rect = rotated_image.get_rect(center=image[0].get_rect(center=(x, y)).center)
    else:
        rotated_image = misc.pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)

    return rotated_image, new_rect


def debug_screen():
    # Debug screen (press F3 to show)
    if misc.DEBUG_SCREEN:
        font = misc.pygame.font.Font(misc.path + "/fonts/font.ttf", 15)
        mouse_x, mouse_y = misc.pygame.mouse.get_pos()

        for gun_man in misc.gunmen:
            if gun_man.is_alive:
                distance = math.sqrt((player.x - gun_man.x) ** 2 + (player.y - gun_man.y) ** 2)

                if distance > gun_man.danger_zone:
                    color = "red"
                else:
                    color = "green"

                misc.pygame.draw.circle(misc.display, "dark green", (gun_man.x, gun_man.y), gun_man.danger_zone, 3)
                misc.pygame.draw.line(misc.display, color, (gun_man.x, gun_man.y), (player.x, player.y), 3)
                misc.pygame.draw.circle(misc.display, "yellow", (gun_man.x, gun_man.y), 5)

        misc.pygame.draw.line(misc.display, "purple", (player.x, player.y), (mouse_x, mouse_y), 3)
        misc.pygame.draw.circle(misc.display, "yellow", (player.x, player.y), 5)

        # Color info overlay's background
        info_bg = misc.pygame.Surface((370, (len(misc.color_list.keys()) * 20) + 50), misc.pygame.SRCALPHA)
        info_bg.fill((0, 0, 0, 128))
        misc.display.blit(info_bg, (0, 0))

        # Title
        title = font.render("DEBUG SCREEN", True, misc.pygame.Color("white"))
        misc.display.blit(title, (10, 10))

        # FPS
        fps = font.render(f"{str(int(misc.clock.get_fps()))} FPS", True, misc.pygame.Color("yellow"))
        misc.display.blit(fps, (295, 10))

        # Show color and its definition
        y_pos = 40
        for color in misc.color_list:
            misc.pygame.draw.rect(misc.display, color, (10, y_pos, 15, 15))
            text = font.render(misc.color_list[color], True, misc.pygame.Color(color))
            misc.display.blit(text, (30, y_pos - 1))
            y_pos += 20


def menu():
    if misc.MENU_OPEN:
        # Using misc.pygame.draw.rect for the menu borders because misc.pygame.Surface doesn't have the border radius setting.
        # Then positioning the misc.pygame.Surface slightly inside the borders so that the corners wouldn't show

        # Menu border
        x, y                 = int(misc.WIDTH / 4), int(misc.HEIGHT / 4)
        width, height        = int(misc.WIDTH / 2), int(misc.HEIGHT / 2)
        border_width, radius = 10, 10

        misc.pygame.draw.rect(misc.display, "white", (x, y, width, height), border_width, border_radius=radius)

        # Menu background
        info_bg = misc.pygame.Surface((int(misc.WIDTH / 2) - 10, int(misc.HEIGHT / 2) - 10), misc.pygame.SRCALPHA)
        info_bg.fill((0, 0, 0, 200))
        misc.display.blit(info_bg, (int(misc.WIDTH / 4) + 5, int(misc.HEIGHT / 4) + 5))

        # Title
        title_font = misc.pygame.font.Font(misc.path + "/fonts/pixel_font.ttf", int(misc.HEIGHT/20))
        title = title_font.render("MENU", True, misc.pygame.Color("white"))
        title_rect = title.get_rect(center=(int(misc.WIDTH / 2), int(misc.HEIGHT / 4) + 60))
        misc.display.blit(title, title_rect)


def show_menu_options(event):
    if misc.MENU_OPEN:
        y_pos = 0
        space_between_options = int(misc.HEIGHT/20)

        for option in misc.menu_options.keys():
            option_font = misc.pygame.font.Font(misc.path + "/fonts/pixel_font.ttf", int(misc.HEIGHT/30))
            option_text = option_font.render(option, True, misc.pygame.Color(misc.menu_options[option]))

            x = int(misc.WIDTH / 2)
            y = int(misc.HEIGHT / 2) - len(misc.menu_options.keys()) * (space_between_options / len(misc.menu_options.keys())) + y_pos

            option_text_rect = option_text.get_rect(center=(x, y))

            misc.display.blit(option_text, option_text_rect)
            y_pos += space_between_options

            if option_text_rect.collidepoint(misc.pygame.mouse.get_pos()):
                # Highlight Quit option in red
                if option == "Quit":
                    highlight_color = "red"

                    # Simple way of checkin whether to play the button hover sound or not
                    if misc.menu_options[option] != "red":
                        misc.button_hover.play()
                else:
                    highlight_color = misc.menu_highlight_color

                    # Simple way of checkin whether to play the button hover sound or not
                    if misc.menu_options[option] != misc.menu_highlight_color:
                        misc.button_hover.play()

                misc.menu_options[option] = highlight_color
            else:
                misc.menu_options[option] = "white"

            if event.type == misc.pygame.MOUSEBUTTONDOWN and event.button == 1:
                if option_text_rect.collidepoint(misc.pygame.mouse.get_pos()):
                    misc.button_click.play()

                    # Decide what happens when one of the menu options is clicked
                    if option == "Close":
                        misc.MENU_OPEN = False
                    elif option == "Restart":
                        game_setup()
                    elif option == "Quit":
                        exit_game()


def spawn_gunmen():
    misc.gunmen.clear()

    # Create gunman
    for _ in range(5):
        gm_x_pos = random.randint(100, misc.WIDTH - 100)
        gm_y_pos = random.randint(100, misc.HEIGHT - 100)
        gm_danger_zone = 400

        misc.gunmen.append(Gunman(gm_x_pos, gm_y_pos, gm_danger_zone, misc.gunman_images))


def exit_game():
    misc.GAME_RUNNING = False
    misc.pygame.mixer.music.stop()

    misc.pygame.quit()
    exit()


def game_setup():
    global player

    # Create new player
    player = Player(int(misc.WIDTH/2), int(misc.HEIGHT/2), misc.player_images)

    # Spawn misc.gunmen
    spawn_gunmen()

    # Close the menu if it is open when starting the game
    if misc.MENU_OPEN:
        misc.MENU_OPEN = False

    # If the mouse's x position is set to the same position as the player's, the player won't turn
    # towards the cursor until it moves
    misc.pygame.mouse.set_pos((int(misc.WIDTH/2)+1, int(misc.HEIGHT/2)-100))


def draw_background():
    background_img_rect = misc.background_img.get_rect()

    y_pos = 0

    for _ in range(math.ceil(misc.WIDTH/background_img_rect.width)):
        x_pos = 0
        for _ in range(math.ceil(misc.HEIGHT/background_img_rect.height)):
            misc.display.blit(misc.background_img, (x_pos, y_pos))
            x_pos += background_img_rect.width

        y_pos += background_img_rect.height


def update_sliders(event):
    slider.update_sliders(event)

    # Sliders' labels
    font = misc.pygame.font.Font(f"{misc.path}/fonts/font.ttf", 15)
    text = font.render(f"Music Volume: {(music_volume.get_value()*10):.1f}", True, misc.pygame.Color("white"))
    misc.display.blit(text, (music_volume.x + music_volume.width + 20, music_volume.y-5))

    text = font.render(f"SFX Volume: {sfx_volume.get_value():.1f}", True, misc.pygame.Color("white"))
    misc.display.blit(text, (sfx_volume.x + sfx_volume.width + 20, sfx_volume.y - 5))

    # Set music and sound effects' volume
    misc.pygame.mixer.music.set_volume(music_volume.get_value())

    misc.pistol_shoot.set_volume(sfx_volume.get_value())
    misc.pistol_reload.set_volume(sfx_volume.get_value() * 0.8)

    misc.button_hover.set_volume(sfx_volume.get_value() * 0.3)
    misc.button_click.set_volume(sfx_volume.get_value() * 0.5)


def main():
    game_setup()
    misc.pygame.mixer.music.play(-1, 0.0)

    while misc.GAME_RUNNING:
        # Game background
        misc.display.fill("dark green")
        draw_background()

        # misc.display the misc.gunmen
        for gunman in misc.gunmen:
            gunman.show()

        # Show player sight
        if misc.MENU_OPEN:
            misc.pygame.mouse.set_visible(True)
        else:
            misc.pygame.mouse.set_visible(False)
            misc.pygame.draw.circle(misc.display, "red", (misc.pygame.mouse.get_pos()), 5)

        # misc.display the player
        player.show()

        # Debug screen (press F3 to show)
        debug_screen()

        # Menu
        menu()

        # Player movement
        if not misc.MENU_OPEN:
            keys = misc.pygame.key.get_pressed()

            # If the user holds shift key, the player will run faster
            if misc.pygame.key.get_mods() & misc.pygame.KMOD_SHIFT:
                movement_speed = 1
            else:
                movement_speed = 0.5

            # Use WASD for movement
            if keys[misc.pygame.K_w]:
                player.move(0, -movement_speed)
            if keys[misc.pygame.K_a]:
                player.move(-movement_speed, 0)
            if keys[misc.pygame.K_s]:
                player.move(0, movement_speed)
            if keys[misc.pygame.K_d]:
                player.move(movement_speed, 0)

        event = misc.pygame.event.poll()

        if event.type == misc.pygame.QUIT:
            exit_game()

        if misc.MENU_OPEN:
            update_sliders(event)

        # Shoot
        if event.type == misc.pygame.MOUSEBUTTONDOWN and event.button == 1 and not misc.MENU_OPEN:
            if not player.reloading and not player.shooting:
                player.shooting = True
                misc.pistol_shoot.play()

            # Check if the player hit the gunman
            if player.shooting:
                for gunman in misc.gunmen:
                    gunman.hit()

        if event.type == misc.pygame.KEYDOWN:
            # Reload
            if event.key == misc.pygame.K_r and not player.reloading and not misc.MENU_OPEN:
                if not player.shooting:
                    player.reloading = True
                    misc.pistol_reload.play()

            # Open pause menu
            if event.key == misc.pygame.K_ESCAPE:
                misc.MENU_OPEN = not misc.MENU_OPEN

            # Toggle debug screen
            if event.key == misc.pygame.K_F3:
                misc.DEBUG_SCREEN = not misc.DEBUG_SCREEN

        # Show menu options
        if misc.MENU_OPEN:
            show_menu_options(event)

        misc.pygame.display.update()
        misc.clock.tick(misc.FPS)


if __name__ == "__main__":
    exit()
