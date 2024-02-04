#!/usr/bin/env python
import asyncio
import os
import signal

from minipadd.config import AppConfig, PiHoleConfig
from minipadd.display import PaddView
from minipadd.stats import Stats


def ask_exit(loop):
    print("Interrupted: exit")
    loop.stop()


async def update(display, stats):
    sys_stats = stats.get_system_stats()
    ftl_stats = stats.get_ftl_stats()
    display.draw_stats(ftl_stats, sys_stats)


async def repeat(interval, func, *args, **kwargs):
    """Run func every interval seconds.

    If func has not finished before *interval*, will run again
    immediately when the previous iteration finished.

    *args and **kwargs are passed as the arguments to func.
    """
    while True:
        await asyncio.gather(
            func(*args, **kwargs),
            asyncio.sleep(interval))


def main():
    loop = asyncio.get_event_loop()

    app_config = AppConfig(os.environ)
    pihole_conf = PiHoleConfig(app_config)

    display = PaddView(app_config)
    stats = Stats(pihole_conf)

    try:
        f = asyncio.ensure_future(repeat(app_config.REFRESH_PERIOD, update, display, stats))
        loop.add_signal_handler(signal.SIGINT, f.cancel)
        loop.run_until_complete(f)
    except asyncio.CancelledError:
        pass


if __name__ == '__main__':
    main()
