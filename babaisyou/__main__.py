import argparse
import asyncio
from functools import partial
import signal
import sys
import logging


async def start_server(env):
    logging.info("starting server")
    from babaisyou.server.app import Server
    server = await Server.create(env["server"])
    return server


async def start_client(env):
    logging.info("starting client")
    from babaisyou.server.app import Client
    client = await Client.create(env["maps"], env["client"])
    await client.start()
    return client


async def start_solo(env):
    logging.info("starting solo")
    from babaisyou.app import App
    app = await App.create(env["maps"])
    await app.start()
    return app


async def run(env):
    if env.get("server"):
        return await start_server(env)
    elif env.get("client"):
        return await start_client(env)
    else:
        return await start_solo(env)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--maps', help='Map name', default="maps/default.txt")
    parser.add_argument('-s', '--server', nargs='?', const="redis://localhost",
                        help='Start server --server <redis url>')
    parser.add_argument('-c', '--client', nargs='?', const="redis://localhost",
                        help='Join server --client <redis url>')
    args = parser.parse_args()
    env = vars(args)

    logging.basicConfig(filename='app.log', level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(run(env))

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
