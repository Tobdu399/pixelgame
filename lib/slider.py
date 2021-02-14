from lib.misc import pygame, display

sliders = []


class Slider:
    def __init__(self, x, y, width, color, pointer_color, start_value, max_value):
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
        self.pointer_color  = pointer_color
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
        pointer = pygame.draw.circle(display, slider.pointer_color, (slider.pointer_x, slider.pointer_y), slider.pointer_radius)

        if event.type == pygame.MOUSEBUTTONDOWN and not slider.active:
            if pointer.collidepoint(pygame.mouse.get_pos()):
                slider.active = True

        if event.type == pygame.MOUSEBUTTONUP and slider.active:
            slider.active = False

        if pygame.mouse.get_pressed()[0] and slider.active:
            slider.pointer_x = pygame.mouse.get_pos()[0]

            if slider.pointer_x > slider.x + slider.width:
                slider.pointer_x = slider.x + slider.width
            elif slider.pointer_x < slider.x:
                slider.pointer_x = slider.x
