import os
import time

from minipadd.config import AppConfig
from minipadd.display import OledScreen
from minipadd.ftl import get_pihole_token


def main():
    config = AppConfig(os.environ)
    config.PIHOLE_TOKEN = get_pihole_token('/etc/pihole')
    display = OledScreen(config)
    while True:
        display.debug_screen()
        time.sleep(10)


if __name__ == '__main__':
    main()
