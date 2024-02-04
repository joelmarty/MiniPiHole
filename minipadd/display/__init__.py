import datetime
import locale

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from minipadd.config import AppConfig
from minipadd.stats import SystemStats, FtlStats


def make_font(name, size):
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', name))
    return ImageFont.truetype(font_path, size)


FONT_SIZE = 13
FONT_SOURCE = make_font('SourceSansPro-Regular.ttf', FONT_SIZE)


def days_hours_minutes(td):
    return td.days, td.seconds // 3600, (td.seconds // 60) % 60


def num_fmt(value, fmt='%d'):
    return locale.format_string(fmt, value, grouping=True)


class PaddView:

    def __init__(self, app_conf: AppConfig):
        locale.setlocale(locale.LC_ALL, app_conf.LOCALE)
        if app_conf.SCREEN_MOCK:
            from inky import InkyMockPHAT as InkyPHAT
        else:
            from inky import InkyPHAT
        self._display = InkyPHAT(app_conf.SCREEN_COLOR, app_conf.SCREEN_FLIP)
        self._display.set_border(InkyPHAT.WHITE)
        self.margin_h = 2
        self.margin_v = 2
        self._color = self._display.YELLOW
        self._white = self._display.WHITE
        self._black = self._display.BLACK

    def _draw_line(self, canvas: ImageDraw, coords: tuple[int, int], text_items: list[tuple[str, int]]):
        """
        Draw a line of text, starting at coords.
        The text is decribed by a list of [text, color] tuples.
        A whitespace will be inserted between each item.
        """
        cursor_pos = coords[0]
        for item in text_items:
            text = item[0]
            canvas.text((cursor_pos, coords[1]), text, fill=item[1])
            cursor_pos += canvas.textlength(f'{text} ')

    def _draw_progressbar(self, canvas: ImageDraw, coords: tuple[int, int], height: int, value: float):
        pbar_end = (self._display.width - self.margin_h, coords[1] + height)
        pbar_width = pbar_end[0] - coords[0]

        # write outer rectangle
        canvas.rectangle((coords, pbar_end), fill=self._black, outline=self._white, width=1)

        # write inner rectangle
        pbar_inner_start = (coords[0] + 1, coords[1] + 1)
        pbar_inner_end = (pbar_inner_start[0] + pbar_width * value, pbar_end[1] - 1)
        canvas.rectangle((pbar_inner_start, pbar_inner_end), fill=self._color)

    def draw_stats(self, ftl: FtlStats, sys: SystemStats):
        canvas = Image.new('P', (self._display.width, self._display.height), self._black)
        draw = ImageDraw.Draw(canvas)
        draw.font = FONT_SOURCE

        # hostname / ip
        line1_y = self.margin_v
        draw.text((self.margin_h, line1_y), f'{sys.hostname} - {sys.ip}', fill=self._white)

        # uptime, top right corner
        uptime = datetime.timedelta(seconds=sys.uptime)
        uptime_dms = days_hours_minutes(uptime)

        uptime_text = f'{uptime_dms[2]}m'
        if uptime_dms[1] != 0:
            uptime_text = f'{uptime_dms[1]}h ' + uptime_text
        if uptime_dms[0] != 0:
            uptime_text = f'{uptime_dms[0]}d ' + uptime_text
        uptime_textlength = draw.textlength(uptime_text)
        uptime_x = self._display.width - uptime_textlength - self.margin_h
        draw.text((uptime_x, line1_y), uptime_text, fill=self._white)

        line2_y = line1_y + FONT_SIZE + self.margin_v
        # domains blocked
        self._draw_line(draw, (self.margin_h, line2_y), [
            ('blocking:', self._white),
            (num_fmt(ftl.domains_being_blocked), self._color),
            ('domains', self._white)
        ])

        line3_y = line2_y + FONT_SIZE + self.margin_v
        # blocked requests (ads_blocked_today out of dns_queries_today)
        self._draw_line(draw, (self.margin_h, line3_y), [
            ('piholed:', self._white),
            (num_fmt(ftl.ads_blocked_today), self._color),
            ('of', self._white),
            (num_fmt(ftl.dns_queries_today), self._color),
            (f'{ftl.ads_percentage_today:.2%}', self._white)
        ])

        line4_y = line3_y + FONT_SIZE + self.margin_v
        pbar_start = (self.margin_h, line4_y)
        self._draw_progressbar(draw, pbar_start, 10, ftl.ads_percentage_today)

        self._display.set_image(canvas)
        self._display.show()

    def wait_close(self):
        """
        If the display is mocked, wait for the emulator window to close
        :return:
        """
        wait_method = getattr(self._display, "wait_for_window_close", None)
        if callable(wait_method):
            wait_method()
