import math
import random
import os.path
import pickle
from lib import misc
from lib import slider
from lib import message

# Sliders
sfx_volume = slider.Slider(int(misc.WIDTH / 4) + 50, int(misc.HEIGHT / 2) + int(misc.HEIGHT / 4) - 90, 200, "grey", 1, 2)
music_volume = slider.Slider(int(misc.WIDTH / 4) + 50, int(misc.HEIGHT / 2) + int(misc.HEIGHT / 4) - 50, 200, "grey", 0.05, 0.2)

slider.sliders.append(sfx_volume)
slider.sliders.append(music_volume)

# TODO: 1) Collision detection so that the gunmen wouldn't go on top of each other (MAYBE!)
# TODO: 2) Game ending


class Player:
    def __init__(self, x, y, images):
        self.x = x
        self.y = y
        self.images = images
        self.angle  = 0

        self.current_image = self.images["idle"]
        self.counter       = 0
        self.frame         = 0

        self.bullets_remaining = self.clip_size = 30

        self.max_health    = self.health = 100
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

        # Display the player
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
    def __init__(self, x, y, walk_speed, run_speed, images, danger_zone=400, health=100, is_alive=True):
        self.x = x
        self.y = y
        self.images = images
        self.angle  = 0

        self.walk_speed = walk_speed
        self.run_speed  = run_speed

        self.danger_zone     = danger_zone
        self.health          = health
        self.is_alive        = is_alive
        self.player_distance = 0

        self.bullets_remaining = self.clip_size = 30

        self.current_image = self.images["idle"]
        self.counter       = 0
        self.frame         = 0

        self.in_display    = False
        self.shooting      = False
        self.reloading     = False

    def show(self):
        # Check if the gunman is in the display
        if misc.WIDTH-50 > self.x > 50 and misc.HEIGHT-50 > self.y > 50:
            self.in_display = True
        else:
            self.in_display = False

        # Calculate the self.angle in which the gunman is positioned using argus tangent
        w = player.x - self.x
        h = player.y - self.y

        self.player_distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)  # distance to player

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

        # Display the gunman if it is alive
        if self.health > 0:
            misc.display.blit(rotated_img, rotated_img_rect.topleft)

            # Display the health bar if the gunman doesn't have full health
            if self.health != 100:
                health_bar_x = rotated_img_rect.x+(rotated_img_rect.width/2)-50
                health_bar_y = rotated_img_rect.y-15
                health_bar_height = 7

                #    |     x      |      y      | width |    height     |
                bg = (health_bar_x, health_bar_y, 100, health_bar_height)          # Health bar background
                fg = (health_bar_x, health_bar_y, self.health, health_bar_height)  # Health bar foreground

                misc.pygame.draw.rect(misc.display, "red", bg, border_radius=2)
                misc.pygame.draw.rect(misc.display, "green", fg, border_radius=2)
        else:
            # If the gunman died, increase the player's score and its multiplier
            if self.is_alive:
                misc.SCORE += 10 * misc.SCORE_MULTIPLIER
                misc.SCORE_MULTIPLIER += 0.1

            self.is_alive = False

    def animate(self, busy, anim_images, idle_image):
        if busy:
            if self.frame >= len(anim_images):
                self.frame = self.counter = 0
                self.current_image = idle_image
                return False
            else:
                self.current_image = anim_images[self.frame]
                return True

    def shoot(self):
        self.shooting = True
        self.bullets_remaining -= 1
        player.health -= 1

    def reload(self):
        self.reloading           = True
        self.bullets_remaining   = self.clip_size

    def hit(self):
        current_image  = misc.pygame.transform.scale(self.current_image[0], self.current_image[1])
        _, gunman_rect = rotate_image(current_image, self.angle, self.x, self.y)

        if gunman_rect.collidepoint(misc.pygame.mouse.get_pos()):
            self.health -= 20

    def move(self):
        if self.player_distance > 1.5*self.danger_zone:
            speed = self.run_speed
        else:
            speed = self.walk_speed

        if not misc.MENU_OPEN:
            if self.player_distance >= self.danger_zone or not self.in_display:
                if self.player_distance > 0:
                    self.x += (player.x - self.x) * speed / self.player_distance
                    self.y += (player.y - self.y) * speed / self.player_distance


def rotate_image(image, angle, x, y):
    # By default pygame.transform.rotate rotates the image to
    # left so to turn it right instead the self.angle must be multiplied by -1
    angle = angle * -1

    rotated_image = misc.pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)

    return rotated_image, new_rect


def debug_screen():
    # Debug screen (press F3 to show)
    if misc.DEBUG_SCREEN:
        font = misc.pygame.font.Font(f"{misc.path}/fonts/font.ttf", 15)
        mouse_x, mouse_y = misc.pygame.mouse.get_pos()

        for gun_man in misc.gunmen:
            if gun_man.is_alive:
                if gun_man.player_distance > gun_man.danger_zone:
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
        # Using misc.pygame.draw.rect for the menu borders because misc.pygame.Surface doesn't have the border
        # radius setting. Then positioning the misc.pygame.Surface slightly inside the borders so that the corners
        # wouldn't show

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
        title_font = misc.pygame.font.Font(f"{misc.path}/fonts/pixel_font.ttf", int(misc.WIDTH/30))
        title = title_font.render("MENU", True, misc.pygame.Color("white"))
        title_rect = title.get_rect(center=(int(misc.WIDTH / 2), int(misc.HEIGHT / 4) + 60))
        misc.display.blit(title, title_rect)

        # Round
        round_font = misc.pygame.font.Font(f"{misc.path}/fonts/pixel_font.ttf", int(misc.WIDTH/80))
        round_text = round_font.render(f"ROUND {misc.ROUND}", True, misc.pygame.Color("white"))
        misc.display.blit(round_text, (int(misc.WIDTH / 4) + 50, title_rect.y))


def show_menu_options(event, options):
    y_pos = 0
    space_between_options = int(misc.HEIGHT/20)

    for option in options.keys():
        option_font = misc.pygame.font.Font(f"{misc.path}/fonts/pixel_font.ttf", int(misc.WIDTH/50))
        option_text = option_font.render(option, True, misc.pygame.Color(options[option]))

        x = int(misc.WIDTH / 2)
        y = int(misc.HEIGHT / 2) - len(options.keys()) * (space_between_options / len(options.keys())) + y_pos

        option_text_rect = option_text.get_rect(center=(x, y))

        misc.display.blit(option_text, option_text_rect)
        y_pos += space_between_options

        if option_text_rect.collidepoint(misc.pygame.mouse.get_pos()):
            # Highlight Quit option in red
            if option == "Quit":
                highlight_color = "red"

                # Simple way of checkin whether to play the button hover sound or not
                if options[option] != "red":
                    misc.pygame.mixer.find_channel(True).play(misc.button_hover)
            else:
                highlight_color = misc.menu_highlight_color

                # Simple way of checkin whether to play the button hover sound or not
                if options[option] != misc.menu_highlight_color:
                    misc.pygame.mixer.find_channel(True).play(misc.button_hover)

            options[option] = highlight_color
        else:
            options[option] = "white"

        if event.type == misc.pygame.MOUSEBUTTONDOWN and event.button == 1:
            if option_text_rect.collidepoint(misc.pygame.mouse.get_pos()):
                misc.pygame.mixer.find_channel(True).play(misc.button_click)

                # Decide what happens when one of the menu options is clicked
                if misc.START_MENU_OPEN:
                    if option == "Start New Game":
                        game_setup()
                    elif option == "Load Previous Game":
                        load_previous_game()

                    if option == "Quit":
                        exit_game()

                if misc.MENU_OPEN:
                    if option == "Close":
                        misc.MENU_OPEN = False
                    elif option == "Restart Game":
                        game_setup()

                    if option == "Save And Quit":
                        save_game_progress()
                        exit_game()


def load_previous_game():
    # These options should be found from the save file
    required_options = ["score", "score multiplier", "round",
                        "player position", "ammo", "health",
                        "gunmen", "gunmen amount"]

    if os.path.isfile(f"{misc.path}/data.dat"):
        save_file_verified = True
        save_file = open(f"{misc.path}/data.dat", "rb")

        try:
            game_progress = pickle.load(save_file)
            save_file.close()

            if isinstance(game_progress, dict):
                for required_option in required_options:
                    if required_option not in game_progress.keys():
                        save_file_verified = False
            else:
                save_file_verified = False

            if save_file_verified:
                game_setup(game_progress)
                print("\nGame loaded successfully!")

        except:
            # If an exception occurs, the save file must be corrupted
            print("\nUnable to load game! The save file of the previous game might be corrupted.")
    else:
        print("\nNo previous game found!")


def save_game_progress():
    gunmen_stats = []
    for gunman in misc.gunmen:
        gunmen_stats.append((gunman.x, gunman.y, gunman.walk_speed, gunman.run_speed, gunman.danger_zone, gunman.health, gunman.is_alive))

    game_progress = {
        "score":            misc.SCORE,
        "score multiplier": misc.SCORE_MULTIPLIER,
        "round":            misc.ROUND,
        "player position":  (player.x, player.y),
        "ammo":             player.bullets_remaining,
        "health":           player.health,
        "gunmen":           gunmen_stats,
        "gunmen amount":    misc.GUNMEN_AMOUNT,
    }

    save_file = open(f"{misc.path}/data.dat", "wb")
    pickle.dump(game_progress, save_file)
    save_file.close()


def new_round():
    global msg

    all_killed = True
    for gunman in misc.gunmen:
        if gunman.is_alive:
            all_killed = False

    if all_killed:
        misc.ROUND            += 1
        misc.GUNMEN_AMOUNT    += 5
        msg = message.Message(f"ROUND {misc.ROUND}")

        misc.gunmen.clear()

        # Create gunman
        for _ in range(misc.GUNMEN_AMOUNT):
            top_or_bottom = random.randint(0, 2)
            left_or_right = random.randint(0, 1)

            gm_danger_zone = random.randint(350, 450)
            gm_walk_speed  = random.uniform(0.1, 0.3)
            gm_run_speed   = random.uniform(0.4, 0.8)

            # Randomize position for the gunman
            spawn_distance = random.randint(0, 400)

            if top_or_bottom == 2:
                gm_y_pos = (misc.HEIGHT+100) + gm_danger_zone + spawn_distance
                gm_x_pos = random.randint(-100 - gm_danger_zone - spawn_distance, (misc.WIDTH+100) + gm_danger_zone + spawn_distance)
            elif top_or_bottom == 1:
                gm_y_pos = random.randint(-100 - gm_danger_zone - spawn_distance, (misc.HEIGHT+100) + gm_danger_zone + spawn_distance)
                if left_or_right == 1:
                    gm_x_pos = (misc.WIDTH+100) + gm_danger_zone + spawn_distance
                else:
                    gm_x_pos = -100 - gm_danger_zone - spawn_distance
            else:
                gm_y_pos = -100 - gm_danger_zone - spawn_distance
                gm_x_pos = random.randint(-100 - gm_danger_zone - spawn_distance, (misc.WIDTH+100) + gm_danger_zone + spawn_distance)

            misc.gunmen.append(Gunman(gm_x_pos, gm_y_pos, gm_walk_speed, gm_run_speed, misc.gunman_images, gm_danger_zone))


def exit_game():
    misc.pygame.mixer.music.stop()
    misc.GAME_OPEN = False


def game_setup(*args):
    global player, msg

    misc.FADE_ALPHA = 255
    misc.FADE_IN    = True

    misc.START_MENU_OPEN = False
    misc.GAME_RUNNING = True

    misc.pygame.mixer.music.fadeout(500)                 # Fade out the previous music
    misc.pygame.mixer.music.load(f"{misc.path}/music/music.wav")
    misc.pygame.mixer.music.play(-1, 0.0, fade_ms=2000)  # Fade in the game background music

    # Create new player
    player = Player(int(misc.WIDTH / 2), int(misc.HEIGHT / 2), misc.player_images)

    # Check if the previous game is trying to be loaded and if so, set the stats as they were in the previous game
    if len(args) > 0:
        if isinstance(args[0], dict):
            game_progress = args[0]

            misc.SCORE               = game_progress["score"]
            misc.SCORE_MULTIPLIER    = game_progress["score multiplier"]
            misc.ROUND               = game_progress["round"]
            misc.GUNMEN_AMOUNT       = game_progress["gunmen amount"]
            player.x, player.y       = game_progress["player position"]
            player.health            = game_progress["health"]
            player.bullets_remaining = game_progress["ammo"]

            misc.gunmen.clear()
            for saved_gunman in game_progress["gunmen"]:
                gm_x           = saved_gunman[0]
                gm_y           = saved_gunman[1]
                gm_walk_speed  = saved_gunman[2]
                gm_run_speed   = saved_gunman[3]
                gm_danger_zone = saved_gunman[4]
                gm_health      = saved_gunman[5]
                gm_is_alive    = saved_gunman[6]

                misc.gunmen.append(Gunman(gm_x, gm_y, gm_walk_speed, gm_run_speed, misc.gunman_images, gm_danger_zone, gm_health, gm_is_alive))

            msg = message.Message("Game Loaded")

    else:
        # Spawn gunmen
        misc.SCORE = misc.ROUND = misc.GUNMEN_AMOUNT = 0
        misc.SCORE_MULTIPLIER   = 1
        misc.gunmen.clear()
        new_round()

        # Close the menu if it is open when starting the game
        if misc.MENU_OPEN:
            misc.MENU_OPEN = False

    # If the mouse's x position is set to the same position as the player's, the player won't turn
    # towards the cursor until it moves
    misc.pygame.mouse.set_pos((int(player.x)+1, int(player.y)-100))


def draw_background():
    y_pos = 0

    for _ in range(math.ceil(misc.WIDTH/misc.background_img_rect.width)):
        x_pos = 0
        for _ in range(math.ceil(misc.HEIGHT/misc.background_img_rect.height)):
            misc.display.blit(misc.background_img, (x_pos, y_pos))
            x_pos += misc.background_img_rect.width

        y_pos += misc.background_img_rect.height


def update_sliders(event):
    slider.update_sliders(event)

    # Sliders' labels
    font = misc.pygame.font.Font(f"{misc.path}/fonts/pixel_font.ttf", 15)

    text = font.render("SFX Volume", True, misc.pygame.Color("white"))
    misc.display.blit(text, (sfx_volume.x + sfx_volume.width + 20, sfx_volume.y - 2.5))

    text = font.render("Music Volume", True, misc.pygame.Color("white"))
    misc.display.blit(text, (music_volume.x + music_volume.width + 20, music_volume.y - 2.5))

    # Set music and sound effects' volume
    misc.pygame.mixer.music.set_volume(music_volume.get_value())

    misc.pistol_shoot.set_volume(sfx_volume.get_value() * 0.6)
    misc.pistol_reload.set_volume(sfx_volume.get_value() * 0.2)

    misc.rifle_shoot.set_volume(sfx_volume.get_value() * 0.8)
    misc.rifle_reload.set_volume(sfx_volume.get_value() * 0.1)

    misc.pistol_empty.set_volume(sfx_volume.get_value() * 0.1)

    misc.button_hover.set_volume(sfx_volume.get_value() * 0.05)
    misc.button_click.set_volume(sfx_volume.get_value() * 0.2)


def show_player_status():
    # Health
    health_bar_width, health_bar_height = 250, 20
    health_remaining = int(player.max_health * (health_bar_width / player.max_health)) - \
                       int((player.max_health - player.health) * (health_bar_width / player.max_health))

    health_x = misc.WIDTH - health_bar_width-20
    health_y = 20

    misc.pygame.draw.rect(misc.display, "red", (health_x, health_y, health_bar_width, health_bar_height))
    misc.pygame.draw.rect(misc.display, "green", (health_x, health_y, health_remaining, health_bar_height))

    font = misc.pygame.font.Font(f"{misc.path}/fonts/font.ttf", 15)
    text = font.render(str(player.health), True, misc.pygame.Color("black"))
    text_rect = text.get_rect(center=(health_x + health_bar_width / 2, health_y + health_bar_height / 2))
    misc.display.blit(text, text_rect)

    # Ammo
    font = misc.pygame.font.Font(f"{misc.path}/fonts/font.ttf", 35)
    text = font.render(f"{player.bullets_remaining} / {player.clip_size}", True, misc.pygame.Color("white"))
    text_rect = text.get_rect(center=(health_x + health_bar_width/2, health_y+50))
    misc.display.blit(text, text_rect)

    # Score
    font = misc.pygame.font.Font(f"{misc.path}/fonts/pixel_font.ttf", 35)
    text = font.render(f"Score {int(misc.SCORE)}", True, misc.pygame.Color("white"))
    misc.display.blit(text, (20, 20))


def show_game():
    # Game background
    draw_background()

    # Display the gunmen
    new_round()

    for gunman in misc.gunmen:
        gunman.move()
        gunman.show()

    # Show player sight
    if misc.MENU_OPEN:
        misc.pygame.mouse.set_visible(True)
    else:
        misc.pygame.mouse.set_visible(False)
        misc.pygame.draw.circle(misc.display, "red", (misc.pygame.mouse.get_pos()), 5)

    # Display the player
    player.show()

    # Show player stats
    show_player_status()

    # Debug screen (press F3 to show)
    debug_screen()

    # Popup Message (current round message)
    if not misc.MENU_OPEN:
        msg.show()

    # Menu
    menu()


def show_start_menu():
    draw_background()


def fade():
    if misc.FADE_IN:
        if misc.FADE_ALPHA > 0:
            misc.FADE_ALPHA -= 2
        if misc.FADE_ALPHA <= 0:
            misc.FADE_ALPHA = 0
            misc.FADE_IN = False

        fade_effect = misc.pygame.Surface((misc.WIDTH, misc.HEIGHT), misc.pygame.SRCALPHA)
        fade_effect.fill((0, 0, 0, misc.FADE_ALPHA))
        misc.display.blit(fade_effect, (0, 0))


def main():
    # Start the start-menu's background music
    misc.pygame.mixer.music.load(f"{misc.path}/music/start_menu.wav")
    misc.pygame.mixer.music.play(-1, 0.0)
    misc.pygame.mixer.music.set_volume(0.05)

    # Set fade start value and set it to be shown
    misc.FADE_ALPHA = 255
    misc.FADE_IN    = True

    while misc.GAME_OPEN:
        misc.display.fill("dark green")

        event = misc.pygame.event.poll()

        if misc.GAME_RUNNING:
            # Display the game ------------------
            show_game()

            # Player movement -------------------
            if not misc.MENU_OPEN:
                keys = misc.pygame.key.get_pressed()

                # If the user holds shift key, the player will move faster
                if misc.pygame.key.get_mods() & misc.pygame.KMOD_SHIFT:
                    movement_speed = 1
                else:
                    movement_speed = 0.5

                # Move using WASD
                if keys[misc.pygame.K_w]:
                    player.move(0, -movement_speed)
                if keys[misc.pygame.K_a]:
                    player.move(-movement_speed, 0)
                if keys[misc.pygame.K_s]:
                    player.move(0, movement_speed)
                if keys[misc.pygame.K_d]:
                    player.move(movement_speed, 0)

        # Event handling ------------------------
        if event.type == misc.pygame.QUIT:
            exit_game()

        if misc.GAME_RUNNING:
            if not misc.MENU_OPEN:
                # Gunman; Shoot
                for gunman in misc.gunmen:
                    if not misc.MENU_OPEN and gunman.is_alive and gunman.player_distance < gunman.danger_zone:
                        # The change of gunman shooting at the player is 1 in 40
                        if not gunman.shooting and not gunman.reloading and random.randint(0, 40) == 0:
                            # Check if the gunman is in the display before shooting
                            if gunman.in_display:
                                # Shoot and if there are no bullets left, reload
                                if gunman.bullets_remaining > 0:
                                    gunman.shoot()
                                    misc.pygame.mixer.find_channel(True).play(misc.rifle_shoot)
                                else:
                                    gunman.reload()
                                    misc.pygame.mixer.find_channel(True).play(misc.rifle_reload)

                # Player; Shoot
                if event.type == misc.pygame.MOUSEBUTTONDOWN and event.button == 1 and not misc.MENU_OPEN:
                    if not player.reloading and not player.shooting:
                        if player.bullets_remaining > 0:
                            player.shooting = True
                            player.bullets_remaining -= 1
                            misc.pygame.mixer.find_channel(True).play(misc.pistol_shoot)
                        else:
                            misc.pygame.mixer.find_channel(True).play(misc.pistol_empty)

                        # Check if the player hit the gunman
                        if player.shooting:
                            for gunman in misc.gunmen:
                                gunman.hit()

                if event.type == misc.pygame.KEYDOWN:
                    # Reload
                    if event.key == misc.pygame.K_r and not player.reloading and not misc.MENU_OPEN:
                        if not player.shooting and player.bullets_remaining < player.clip_size:
                            player.reloading = True
                            player.bullets_remaining = player.clip_size
                            misc.pygame.mixer.find_channel(True).play(misc.pistol_reload)

            # Show menu options
            if misc.MENU_OPEN:
                update_sliders(event)
                show_menu_options(event, misc.menu_options)

            if event.type == misc.pygame.KEYDOWN:
                # Open and Close the pause menu
                if event.key == misc.pygame.K_ESCAPE:
                    misc.MENU_OPEN = not misc.MENU_OPEN
                    misc.pygame.mixer.find_channel(True).play(misc.button_hover)

                # Toggle debug screen
                if event.key == misc.pygame.K_F3:
                    misc.DEBUG_SCREEN = not misc.DEBUG_SCREEN

        # Show start menu
        if misc.START_MENU_OPEN:
            # show_start_menu()
            misc.display.blit(misc.start_menu_background_img, (0, 0))
            show_menu_options(event, misc.start_menu_options)

        # Show fade effect
        fade()

        # Update the screen
        misc.pygame.display.update()
        misc.clock.tick(misc.FPS)


if __name__ == "__main__":
    exit()
