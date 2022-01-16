# %%
import ast
import asyncio
import dataclasses
import os
from datetime import datetime
from pprint import pprint
from time import time
from typing import *

import aiohttp
import discord
import requests

from discord.message import Message
from dotdict import dotdict
from dotenv import load_dotenv
from requests import models

from senseibot.commands import *
from senseibot.commands.BaseRunner import BaseRunner
from senseibot.commands.Timer import TIMERSTATES, CANCELLED
from senseibot.logger import logger, set_log_level
from senseibot.utils import all_subclasses, notify_callback, send_text

set_log_level("DEBUG")
load_dotenv()

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
HEADERS = {"Authorization": f"Bot {DISCORD_TOKEN}"}
SHARE_URL = os.environ["SHARE_URL"]


client = discord.Client()
all_commands = all_subclasses(BaseRunner)


@client.event
async def on_ready():
    logger.info("We have logged in as {0.user}".format(client))
    await client.change_presence(activity=discord.Game("Python"))  # Pythonをプレイ中


@client.event
async def on_socket_response(socket_response):

    if socket_response["t"] != "INTERACTION_CREATE":
        return

    channel_id = socket_response["d"]["channel_id"]
    custom_id = socket_response["d"]["data"].get("custom_id", None)
    if custom_id.startswith("button"):
        event_type, *args = custom_id.split("_")
    elif custom_id.startswith("guitimer"):
        event_type, *args = custom_id.split("_")
    else:
        return

    logger.info(f"Received event with custom_id: {custom_id}")
    n_args = len(args)

    command = args[0] if n_args > 0 else "summon"
    command_args = args[1:]  # 空の可能性あり

    # Run button
    if event_type == "button":
        runner = all_commands[command](client, channel_id)
        logger.info(f"Running command: {command} {*command_args, }")
        await runner.run(command_args)
    
    # Run GUITimer
    if event_type == "guitimer":
        global TIMERSTATES
        global CANCELLED
        _id = command_args[-1]
        value = socket_response["d"]["data"].get("values", [None])[0]
        logger.info(f"Configure GUITIMER@{_id}: {command} {*command_args, value}")
        
        if command == "del":
            if CANCELLED[_id]:
                await send_text(f"何回も'Stop Timer'押さないでよ、壊そうとしないでくれ...これでも一生懸命作ったんだ（泣", client, channel_id)      
            else:
                CANCELLED[_id] = True
                await send_text(f"タイマーを削除しました。", client, channel_id)      
        if command == "rest":
            TIMERSTATES[_id].rest = int(value)
        if command == "study":
            TIMERSTATES[_id].study = int(value)
        if command == "repeat":
            TIMERSTATES[_id].repeat = int(value)
        if command == "start":
            runner = all_commands["starttimermin"](client, channel_id)
            await notify_callback(socket_response["d"]["id"], socket_response["d"]["token"])
            await runner.run(_id)
            return
        
    await notify_callback(socket_response["d"]["id"], socket_response["d"]["token"])
    return

    # channel_id = button_click["d"]["channel_id"]
    # custom_id = button_click["d"]["data"]["custom_id"]
    # normal_url = returnNormalUrl(button_click["d"]["channel_id"])

    # prefix: List[str] = custom_id.split("_")
    # _id = custom_id.split("_")[-1]
    # if prefix[0] == "del":
    #     global CANCELLED
    #     CANCELLED[_id] = True
    #     json = {"content": f"タイマー {_id} は削除されました。"}
    #     r = requests.post(normal_url, headers=HEADERS, json=json)
    # elif prefix[0] == "menu":
    #     global TIMERSTATES
    #     if prefix[1] == "start":
    #         TIMERSTATES[_id].start = True
    #     else:
    #         value = button_click["d"]["data"]["values"][0]  # 単一選択なので要素1つのリストが返る
    #         if prefix[1] == "rest":
    #             TIMERSTATES[_id].rest = int(value)
    #         if prefix[1] == "study":
    #             TIMERSTATES[_id].study = int(value)
    #         if prefix[1] == "repeat":
    #             TIMERSTATES[_id].repeat = int(value)
    #         json = {"content": f"[DEBUG]: {value}, {custom_id}"}
    #         r = requests.post(normal_url, headers=HEADERS, json=json)
    # elif prefix[0] == "help":
    #     if prefix[1] == "helpall":
    #         await HelpAll().run(channel_id=channel_id)
    #     if prefix[1] == "share":
    #         await Share().run(channel_id=channel_id)
    #     if prefix[1] == "guitimer":
    #         await GUITimer().run(channel_id=channel_id)
    #     if prefix[1] == "calendar":
    #         await Calendar().run(channel_id=channel_id)
    # await notify_callback(button_click["d"]["id"], button_click["d"]["token"])


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    if not (client.user.mentioned_in(message) and len(message.mentions) == 1):
        return

    contents = message.clean_content
    mention, *args = contents.split(" ")
    n_args = len(args)
    logger.info(f"Received message: {contents}")
    logger.info(f"Interpreting {len(args)} args: {args}")

    channel_id = message.channel.id

    command = args[0] if n_args > 0 else "summon"
    command_args = args[1:]  # 空の可能性あり
    runner = all_commands[command](client, channel_id)
    logger.info(f"Running command: {command} {*command_args, }")
    await runner.run(command_args)


def main():
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
