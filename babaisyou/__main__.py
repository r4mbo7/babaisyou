import asyncio
import sys
from app import App

async def run():
    app = await App.create()
    app.start()
    return 0


def main():
    loop = asyncio.get_event_loop()
    try:
        return loop.run_until_complete(run())
    except Exception as exc:
        raise exc
    finally:
        loop.close()


if __name__ == '__main__':
    sys.exit(main())
