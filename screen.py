from pygame import display, HWSURFACE, DOUBLEBUF, Color, draw, key, gfxdraw
import os

PIXEL_WIDTH = 64
PIXEL_HEIGHT = 32

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)


class C8screen:

    def __init__(self, scale):
        self.scale          = scale
        self.surface        = None

        os.environ['SDL_VIDEO_CENTERED'] = "1"

        display.init()
        self.surface = display.set_mode(
            (PIXEL_WIDTH * self.scale,
             PIXEL_HEIGHT * self.scale))
        display.set_caption('Pychee')

    def update(self, gfx):
        self.surface.fill(BLACK)

        for y, y_list in enumerate(gfx):
            y *= self.scale
            for x, pixel in enumerate(y_list):
                if pixel == 1:
                    x *= self.scale
                    draw.rect(self.surface, WHITE, (x, y, self.scale, self.scale))

        display.update()