""" Manage the game for mutliplayer parties """
import aioredis
import asyncio
import logging
import time
from functools import partial
from babaisyou.app import App
from babaisyou.items import You, P1, P2

SERVER_CHANNEL = "server"
CLIENT_CHANNEL = "client"

directions = {
    "move_up": 0,
    "move_right": 1,
    "move_down": 2,
    "move_left": 4,
}


class Server(object):
    """docstring for Server"""

    def __init__(self, pub, sub):
        self.clients = set([1, 2])
        self.pub = pub
        self.sub = sub
        self._close_future = asyncio.Future()
        self._worker_task = asyncio.ensure_future(self.worker())

    @classmethod
    async def create(cls, host="redis://localhost"):
        pub = await aioredis.create_redis(host)
        sub = await aioredis.create_redis(host)
        server = cls(pub, sub)
        logging.info("Server up !")
        return server

    async def worker(self):
        logging.debug("Server worker start !")
        res = await self.sub.subscribe(SERVER_CHANNEL)
        ch = res[0]
        while (await ch.wait_message()):
            msg = await ch.get_json()
            print(f"Got Message: {msg}")
            if "hello" in msg:
                # new player
                await self.register_client(msg["hello"])
            elif "bye" in msg:
                await self.disconnect_client(msg["bye"])
            elif "move" in msg:
                await self.receiv_move(**msg["move"])

    async def register_client(self, timestamp):
        # a new player join the server
        if len(self.clients) <= 0:
            logging.warning("max 2 players")
            return

        client_id = self.clients.pop()
        await self.pub.publish_json(CLIENT_CHANNEL, {"hello": timestamp, "client_id": client_id})

    async def disconnect_client(self, client_id):
        # a client is leaving the server
        self.clients.add(client_id)

    async def shutdown(self):
        # shutdown server → disconnect clients
        await self.pub.publish_json(CLIENT_CHANNEL, "bye")

    async def receiv_move(self, client_id, direction):
        # receiv a move from the client
        await self.broadcast_move(client_id, direction)

    async def broadcast_move(self, client_id, direction):
        # broadcast the move of client to all clients
        await self.pub.publish_json(CLIENT_CHANNEL,
                                    {"move": {"client_id": client_id, "direction": direction}})

    def close(self):
        if not self._close_future.done():
            self._close_future.set_result(None)

    async def wait_closed(self):
        await self._close_future
        await self.sub.unsubscribe(SERVER_CHANNEL)
        await self._worker_task
        self.sub.close()
        self.pub.close()


class Client(object):

    def __init__(self, pub, sub, app):
        self.pub = pub
        self.sub = sub
        self.app = app
        self.client_id = int(time.time())
        self.loop = asyncio.get_event_loop()
        self._close_future = asyncio.Future()
        self._client_id_future = asyncio.Future()
        self._worker_task = asyncio.ensure_future(self.worker())

    @classmethod
    async def create(cls, maps, host="redis://localhost"):
        # register to server
        pub = await aioredis.create_redis(host)
        sub = await aioredis.create_redis(host)
        app = await App.create(maps)
        client = cls(pub, sub, app)
        app.quit = client.disconnect_to_server
        app.gui.register_actions(quit=app.quit,
                                 up=partial(client.send_move, directions["move_up"]),
                                 down=partial(client.send_move, directions["move_down"]),
                                 left=partial(client.send_move, directions["move_left"]),
                                 right=partial(client.send_move, directions["move_right"]),
                                 retry=app.retry)
        logging.debug("Client created !")
        return client

    async def start(self):
        await self.pub.publish_json(SERVER_CHANNEL, {"hello": self.client_id})
        await self._client_id_future
        if self.client_id == 1:
            P1.apply_actions = You.apply_actions
        else:
            P2.apply_actions = You.apply_actions
        self.app.read_rules()
        await self.app.start()

    async def worker(self):
        logging.debug("Client worker start !")
        res = await self.sub.subscribe(CLIENT_CHANNEL)
        ch = res[0]
        while (await ch.wait_message()):
            msg = await ch.get_json()
            logging.debug(f"CLIENT Got message: {msg}")

            if "hello" in msg and msg["hello"] == self.client_id:
                self.client_id = msg["client_id"]
                logging.debug(f"Got client id : {self.client_id}")
                self._client_id_future.set_result(self.client_id)

            elif "bye" in msg:
                await self.server_shutdown()

            elif "move" in msg:
                await self.receiv_move(**msg["move"])

    async def disconnect_to_server(self):
        # quit the server
        await self.pub.publish_json(SERVER_CHANNEL, {"bye": self.client_id})
        self.close()

    async def server_shutdown(self):
        # server is shutting down
        self.app.quit("server disconnection")
        self.close()

    async def send_move(self, direction):
        # forward player move to server
        logging.debug(f"Send {direction}")
        msg = {"move": {"client_id": self.client_id, "direction": direction}}
        await self.pub.publish_json(SERVER_CHANNEL, msg)

    async def receiv_move(self, client_id, direction):
        # receive the move from a client
        for move, index in directions.items():
            if index == direction:
                move = getattr(self.app, move)
                if client_id == 1:
                    await move(lambda item: item.p1)
                else:
                    await move(lambda item: item.p2)

    def close(self):
        if not self._close_future.done():
            self._close_future.set_result(None)

    async def wait_closed(self):
        await self._close_future
        await self.app.quit()
        self.app.close()
        await self.app.wait_closed()
        await self.sub.unsubscribe(CLIENT_CHANNEL)
        await self._worker_task
        self.sub.close()
        self.pub.close()
