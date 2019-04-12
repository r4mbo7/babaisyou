import asyncio
from app import App
from functools import partial
import signal
import sys
import logging


async def run():
    app = await App.create()
    await app.start()
    return app


def main():
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    logging.info('Game on !')

    loop = asyncio.get_event_loop()

    app = loop.run_until_complete(run())

    def shutdown(sig):
        logging.info('received signal %s, shutting down', sig)
        app.close()

    loop.add_signal_handler(signal.SIGINT, partial(shutdown, 'SIGINT'))
    loop.add_signal_handler(signal.SIGTERM, partial(shutdown, 'SIGTERM'))

    loop.run_until_complete(app.wait_closed())
    loop.close()

    logging.info('game over')


if __name__ == '__main__':
    sys.exit(main())
