# %%
import os
import discord
from dotenv import load_dotenv
from datetime import datetime
from time import time
import ast
from typing import *
from dotdict import dotdict
import asyncio
from collections import defaultdict
from hashlib import md5
# %%

load_dotenv()
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
CANCELLED = defaultdict(bool)

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

def parse2dotdict(command: str, content: str) -> dotdict:
    arg = content[len(command):].strip()
    try:
        arg = ast.literal_eval('{'+arg+'}')
    except:
        arg = dict()
    arg = dotdict(arg)
    return arg

def myhash(message: Any) -> str:
    return md5((str(message)+str(time())).encode()).hexdigest()

def check_timer(arg: dotdict) -> bool:
    if not 'countdown_sec' in arg: return False
    if not 'study_sec'     in arg: return False
    if not 'break_sec'     in arg: return False
    if not 'interval_num'  in arg: return False
    if not type(arg.countdown_sec) == int: return False
    if not type(arg.study_sec)     == int: return False
    if not type(arg.break_sec)     == int: return False
    if not type(arg.interval_num)  == int: return False
    return True

async def command_timer(
    message: discord.message.Message,
    arg: dotdict,
    ) -> None:
    """
    sensei timer 'countdown_sec':60, 'study_sec':3600, 'break_sec':600, 'interval_num':2
    """
    global CANCELLED
    _id = myhash(message)
    await message.channel.send('\n'.join([
        f'"id": "{_id}"',
        f'{arg.countdown_sec}秒後にタイマーをセットしました。',
        f'設定は、',
        f'勉強時間が{arg.study_sec}秒',
        f'休憩時間が{arg.break_sec}秒',
        f'回数が{arg.interval_num}回',
        f'です',
    ]))
    await asyncio.sleep(arg.countdown_sec)
    for i in range(1, arg.interval_num+1):
        if CANCELLED[_id]:
            break
        await message.channel.send('\n'.join([
            f'"id": "{_id}"',
            f'{i}回目の勉強時間になりました。',
            f'勉強を{arg.study_sec}秒はじめてください。',
        ]))
        await asyncio.sleep(arg.study_sec)
        if CANCELLED[_id]:
            break
        await message.channel.send('\n'.join([
            f'"id": "{_id}"',
            f'{i}回目の休憩時間になりました。',
            f'休憩を{arg.break_sec}秒とってください。',
        ]))
        await asyncio.sleep(arg.break_sec)
    else:
        if CANCELLED[_id]:
            return
        await message.channel.send('\n'.join([
            f'"id": "{_id}"',
            f'{i}回のインターバルが完了しました。',
            f'お疲れさまでした！',
        ]))

def check_cancel(arg: dotdict) -> bool:
    if not 'id' in arg: return False
    if not type(arg.id) == str: return False
    return True

async def command_cancel(
    message: discord.message.Message,
    arg: dotdict,
    ) -> None:
    """
    sensei cancel "id": "2bb8638717f17e44a3726afd245445c2"
    """
    global CANCELLED
    CANCELLED[arg.id] = True
    await message.channel.send('\n'.join([
        f'"id": "{arg.id}"',
        f'をキャンセルしました',
    ]))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content
    if not content.startswith('sensei '):
        return
    content = message.content[len('sensei '):]

    command = 'debug'
    if content.startswith(command):
        for k in dir(message):
            await message.channel.send(f"【{k}】 {getattr(message, k)}")

    command = 'timer'
    if content.startswith(command):
        arg = parse2dotdict(command, content)
        if check_timer(arg):
            await command_timer(message, arg)
        else:
            await message.channel.send('[USAGE] '+command_timer.__doc__)

    command = 'cancel'
    if content.startswith(command):
        arg = parse2dotdict(command, content)
        if check_cancel(arg):
            await command_cancel(message, arg)
        else:
            await message.channel.send('[USAGE] '+command_cancel.__doc__)

    command = 'start'
    if content.startswith(command):
        await message.channel.send('開始します')

    command = 'halt'
    if content.startswith(command):
        await message.channel.send(f'LifeError: Bot commit suicide')

    command = 'date'
    if content.startswith(command):
        await message.channel.send(f'{datetime.now()}')

def main():
    client.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()
