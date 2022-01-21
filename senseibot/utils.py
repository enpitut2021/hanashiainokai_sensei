import ast
from hashlib import md5
from time import time

import aiohttp
from dotdict import dotdict
from senseibot.logger import logger


def myhash(message):
    return md5((str(message) + str(time())).encode()).hexdigest()


def returnNormalUrl(channelId) -> str:
    return f"https://discordapp.com/api/channels/{channelId}/messages"


async def notify_callback(id, token):
    url = f"https://discord.com/api/v9/interactions/{id}/{token}/callback"
    json = {"type": 6}
    async with aiohttp.ClientSession() as s:
        async with s.post(url, json=json) as r:
            if 200 <= r.status < 300:
                return


def parse2dotdict(content: str) -> dotdict:
    try:
        arg = ast.literal_eval("{" + content + "}")
    except:
        arg = dict()  # type: ignore
    arg = dotdict(arg)
    return arg


async def send_text(msg, client, channel_id):
    logger.debug(msg)
    channel = client.get_channel(int(channel_id))
    logger.info(f"Sending message to channel: {channel}")
    await channel.send(msg)


def all_subclasses(cls):
    def _all_subclasses(cls):
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in _all_subclasses(c)]
        )

    return {subcls.__name__.lower(): subcls for subcls in _all_subclasses(cls)}
