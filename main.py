# %%
import os
import discord
from discord.message import Message
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
CANCELLED: DefaultDict[str, bool]= defaultdict(bool)

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

def parse2dotdict(content: str) -> dotdict:
    try:
        arg = ast.literal_eval('{'+content+'}')
    except:
        arg = dict() # type: ignore
    arg = dotdict(arg)
    return arg

def myhash(message: Any) -> str:
    return md5((str(message)+str(time())).encode()).hexdigest()

class settimer:
    example = "'countdown_sec':60, 'study_sec':3600, 'break_sec':600, 'interval_num':2"
    def check(arg: dotdict) -> bool:
        if not 'countdown_sec' in arg: return False
        if not 'study_sec'     in arg: return False
        if not 'break_sec'     in arg: return False
        if not 'interval_num'  in arg: return False
        if not type(arg.countdown_sec) == int: return False
        if not type(arg.study_sec)     == int: return False
        if not type(arg.break_sec)     == int: return False
        if not type(arg.interval_num)  == int: return False
        return True

    async def run(
        message: Message,
        arg: dotdict,
        ) -> None:
        global CANCELLED
        _id = myhash(message)
        await message.channel.send('\n'.join([
            '```',
            f'\'id\': \'{_id}\'',
            '```',
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
                '```',
                f'\'id\': \'{_id}\'',
                '```',
                f'{i}/{arg.interval_num}回目の勉強時間になりました。',
                f'勉強を{arg.study_sec}秒はじめてください。',
            ]))
            await asyncio.sleep(arg.study_sec)
            if CANCELLED[_id]:
                break
            if i == arg.interval_num:
                continue
            await message.channel.send('\n'.join([
                '```',
                f'\'id\': \'{_id}\'',
                '```',
                f'{i}/{arg.interval_num}回目の休憩時間になりました。',
                f'休憩を{arg.break_sec}秒とってください。',
            ]))
            await asyncio.sleep(arg.break_sec)
        else:
            if CANCELLED[_id]:
                return
            await message.channel.send('\n'.join([
                '```',
                f'\'id\': \'{_id}\'',
                '```',
                f'{arg.interval_num}回のインターバルが完了しました。',
                f'お疲れさまでした！',
            ]))

class unsettimer:
    example = "'id': '2bb8638717f17e44a3726afd245445c2'"
    @staticmethod
    def check(arg: dotdict) -> bool:
        if not 'id' in arg: return False
        if not type(arg.id) == str: return False
        return True

    @staticmethod
    async def run(
        message: Message,
        arg: dotdict,
        ) -> None:
        global CANCELLED
        _id = arg.id
        CANCELLED[_id] = True
        await message.channel.send('\n'.join([
            '```',
            f'\'id\': \'{_id}\'',
            '```',
            f'をキャンセルしました',
        ]))

commands = {
    'settimer': settimer,
    'unsettimer': unsettimer,
}

@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    if not (client.user.mentioned_in(message) and len(message.mentions) == 1):
        return

    contents = message.clean_content.replace('@sensei', '').strip().split()
    if len(contents) > 0 and contents[0] in commands:
        command = contents[0]
        content = ' '.join(contents[1:])
        runner = commands[command]
        arg = parse2dotdict(content)
        if runner.check(arg):
            await runner.run(message, arg)
        else:
            await message.channel.send(f'[USAGE] @sensei {command} {runner.example}')
    else:
        await message.channel.send('[USAGE_DESCRIPTION_TODO]')

#    command = 'date'
#    if content.startswith(command):
#        await message.channel.send(f'{datetime.now()}')

def main():
    client.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()
