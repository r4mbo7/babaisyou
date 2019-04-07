import asyncio
from app import App
import sys
import logging

async def run():
    app = await App.create()
    app.start()
    await app.wait_closed()


def main():
    logging.basicConfig(filename='app.log',level=logging.DEBUG)
    logging.info('Game on !')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    finally:
        loop.close()
        logging.info('game over')


if __name__ == '__main__':
    sys.exit(main())
