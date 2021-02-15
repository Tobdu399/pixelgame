from lib.misc import pygame, display, path

sliders = []


class Slider:
    def __init__(self, x, y, width, color, start_value, max_value):
        self.x = x
        self.y = y
        self.width       = width
        self.height      = 8
        self.color       = color
        self.start_value = start_value
        self.max_value   = max_value

        self.pointer_radius = 8
        self.pointer_x      = self.x + (self.width / self.max_value)*self.start_value
        self.pointer_y      = self.y + self.pointer_radius/2
        self.value          = 0
        self.active         = False

    def show(self):
        pygame.draw.rect(display, self.color, (self.x, self.y, self.width, self.height), border_radius=5)
        self.value = ((self.pointer_x - self.x) / self.width) * self.max_value  # Update the slider value
        # Slider's pointer is drawn in the move_pointer

    def get_value(self):
        return self.value


def update_sliders(event):
    for slider in sliders:
        slider.show()

        # Slider's pointer color
        r = ((slider.pointer_x - slider.x) / slider.width) * 255
        g = 255 - ((slider.pointer_x - slider.x) / slider.width) * 255
        b = 0

        # Show slider
        pointer = pygame.draw.circle(display, (r, g, b), (slider.pointer_x, slider.pointer_y), slider.pointer_radius)

        if slider.active:
            font = pygame.font.Font(f"{path}/fonts/pixel_font.ttf", 15)
            text = font.render(f"{(((slider.pointer_x - slider.x) / slider.width) * 100):.0f}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(slider.pointer_x, slider.pointer_y-20))
            display.blit(text, text_rect)

        # Check if the slider's pointer is clicked
        if event.type == pygame.MOUSEBUTTONDOWN and not slider.active:
            if pointer.collidepoint(pygame.mouse.get_pos()):
                slider.active = True

        # Check if the slider's pointer is no longer used
        if event.type == pygame.MOUSEBUTTONUP and slider.active:
            slider.active = False

        # If the slider's pointer is active move it to the cursor's position
        if pygame.mouse.get_pressed(3)[0] and slider.active:
            slider.pointer_x = pygame.mouse.get_pos()[0]

            # Make sure that the slider's pointer is inside the slider
            if slider.pointer_x > slider.x + slider.width:
                slider.pointer_x = slider.x + slider.width
            elif slider.pointer_x < slider.x:
                slider.pointer_x = slider.x
