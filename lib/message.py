from lib.misc import pygame, display, path, WIDTH, HEIGHT


class Message:
    def __init__(self, message):
        self.message          = message
        self.duration         = 750 # ~6 seconds
        self.frame            = 0
        self.max_transparency = self.transparency = 255

    def show(self, fade_out_speed=5):
        if self.frame < self.duration:
            # Text
            font = pygame.font.Font(f"{path}/fonts/pixel_font.ttf", int(WIDTH/20))
            text = font.render(self.message, True, pygame.Color("white"))
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))

            # Make a fade-out effect for the text
            if self.transparency < 0:   # Make sure the transparency value isn't less than 0
                self.transparency = 0

            alpha_img = pygame.Surface(text.get_size(), pygame.SRCALPHA)
            alpha_img.fill((255, 255, 255, self.transparency))
            text.blit(alpha_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            display.blit(text, text_rect)

            self.frame += 1
            if self.duration - self.frame <= self.max_transparency:
                self.transparency -= fade_out_speed
