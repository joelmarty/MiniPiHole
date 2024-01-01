import os
from pathlib import Path

from minipadd.config import AppConfig

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.sprite_system import framerate_regulator
from luma.oled.device import ssd1322
from luma.core.virtual import terminal

from PIL import ImageFont, Image, ImageDraw


def make_font(name, size):
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', name))
    return ImageFont.truetype(font_path, size)


class OledScreen:
    def __init__(self, config: AppConfig):
        self.config = config
        if config.HEADLESS_MODE:
            serial = noop()
        else:
            serial = spi(port=0)
        self.device = ssd1322(serial, mode="1", rotate=config.SCREEN_ROTATION)
        self.font = make_font('Dot Matrix Regular.ttf', 10)
        self.width = 256
        self.height = 64
        self.regulator = framerate_regulator(config.SCREEN_TARGET_FPS)

    def debug_screen(self):
        term = terminal(self.device, self.font)
        term.println('=== Display ===')
        term.println(f'refresh = {self.config.REFRESH_PERIOD}s')
        term.println(f"target fps = {self.config.SCREEN_TARGET_FPS}")
        term.println(f"rotation = {self.config.SCREEN_ROTATION}")
        term.println("=== PiHole ===")
        term.println(f"target = {self.config.PIHOLE_HOST}:{self.config.PIHOLE_PORT}")
        term.println(f"token = {self.config.PIHOLE_TOKEN}")
        term.flush()
