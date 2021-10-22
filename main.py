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
import requests
from discord.ext import commands
from pprint import pprint
import aiohttp
import dataclasses
# %% グローバル変数（大文字）

load_dotenv()
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
HEADERS = { "Authorization": f"Bot {DISCORD_TOKEN}" }
SHARE_URL = os.environ['SHARE_URL']

CANCELLED: DefaultDict[str, bool] = defaultdict(bool)

@dataclasses.dataclass
class TimerState:
    study: int = 25
    rest: int = 5
    repeat: int = 3
    start: bool = False

TIMERSTATES = defaultdict(TimerState)

REPEAT_MAX = 10
STUDY_MAX = 24*60*60
REST_MAX = 24*60*60

# %% 通常の関数
def returnNormalUrl(channelId) -> str:
    return f"https://discordapp.com/api/channels/{channelId}/messages"

async def notify_callback(id, token):
    url = f"https://discord.com/api/v9/interactions/{id}/{token}/callback"
    json = { "type": 6 }
    async with aiohttp.ClientSession() as s: # TODO わからん
        async with s.post(url, json=json) as r:
            if 200 <= r.status < 300:
                return

def parse2dotdict(content: str) -> dotdict:
    try:
        arg = ast.literal_eval('{'+content+'}')
    except:
        arg = dict() # type: ignore
    arg = dotdict(arg)
    return arg

def myhash(message: Any) -> str:
    return md5((str(message)+str(time())).encode()).hexdigest()

class Commands(dict):
    def __call__(self, runner):
        self[runner.__name__.lower()] = runner
        return runner
commands = Commands()

# %% コマンドを定義するクラス

class BaseRunner:
    def __init__(self):
        self.example: dotdict = dotdict()
        self.arg_comment = dotdict()
        self.func_comment: List[str] = list()
    def check(self, arg: dotdict) -> bool:
        return True
    async def run(
        self,
        message: Message,
        arg: dotdict,
        ) -> None:
        return
    def _description(
        self,
        message: Message,
        command: str,
        ) -> str:
        return '\n'.join(
        [f'**{command} コマンドの説明**']+[
            f'> {txt}'
            for txt in self.func_comment
        ]+['引数の説明']+[
            f"    `'{arg}'`: {self.arg_comment[arg]}"
            for arg in self.arg_comment
        ]+[f'実行例']+[
            '```',
            f'@sensei {command} {str(self.example)[1:][:-1]}',
            '```',
        ])
    async def description(
        self,
        message: Message,
        command: str,
        ) -> None:
        await message.channel.send( self._description(message, command) )

@commands
class StartTimerSec(BaseRunner):
    def __init__(self):
        super().__init__()
        self.unit_int = 1
        self.unit_str = '秒'
        self.example = dotdict({'countdown':0, 'study':1, 'rest':1, 'repeat':2})
        self.arg_comment = dotdict({'countdown':f'開始までの{self.unit_str}数', 'study':f'勉強する{self.unit_str}数', 'rest':f'休憩する{self.unit_str}数', 'repeat':'インターバルの回数'})
        self.func_comment = [
            '勉強＆休憩の間隔をタイマーが通知して支援してくれるコマンドです。',
            f'極端な値の入力は弾かれる場合があります。',
        ]

    def check(self, arg: dotdict) -> bool:
        if not 'countdown' in arg: return False
        if not 'study'     in arg: return False
        if not 'rest'      in arg: return False
        if not 'repeat'    in arg: return False
        if not type(arg.countdown) == int: return False
        if not type(arg.study)     == int: return False
        if not type(arg.rest)      == int: return False
        if not type(arg.repeat)    == int: return False
        if not self.unit_int * arg.study  in range(STUDY_MAX) : return False
        if not self.unit_int * arg.rest   in range(REST_MAX)  : return False
        if not                 arg.repeat in range(REPEAT_MAX): return False
        return True

    async def run(
        self,
        message: Message,
        arg: dotdict,
        _id: str = None,
        ) -> None:
        global CANCELLED
        if _id == None:
            _id = myhash(message)
        await message.channel.send('\n'.join([
            '```',
            f'@sensei stoptimer \'id\': \'{_id}\'',
            '```',
            f'{arg.countdown}{self.unit_str}後にタイマーをセットしました。',
            f'設定は、',
            f'勉強時間が{arg.study}{self.unit_str}',
            f'休憩時間が{arg.rest}{self.unit_str}',
            f'回数が{arg.repeat}回',
            f'です',
        ]))
        # %%
        normal_url = returnNormalUrl(message.channel.id)
        json = {
            "content": "以下のボタンでタイマーストップできます",
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "label": "Stop Timer",
                            "style": 1,
                            "custom_id": f"del_{_id}",
                        },
                    ]

                }
            ]
        }
        r = requests.post(normal_url, headers=HEADERS, json=json)
        # TODO requests.postの合否判定が必要か？
        # %%
        await asyncio.sleep(arg.countdown*self.unit_int)
        for i in range(1, arg.repeat+1):
            if CANCELLED[_id]:
                break
            await message.channel.send('\n'.join([
                '```',
                f'@sensei stoptimer \'id\': \'{_id}\'',
                '```',
                f'{i}/{arg.repeat}回目の勉強時間になりました。',
                f'勉強を{arg.study}{self.unit_str}はじめてください。',
            ]))
            await asyncio.sleep(arg.study*self.unit_int)
            if CANCELLED[_id]:
                break
            if i == arg.repeat:
                continue
            await message.channel.send('\n'.join([
                '```',
                f'@sensei stoptimer \'id\': \'{_id}\'',
                '```',
                f'{i}/{arg.repeat}回目の休憩時間になりました。',
                f'休憩を{arg.rest}{self.unit_str}とってください。',
            ]))
            await asyncio.sleep(arg.rest*self.unit_int)
        else:
            if CANCELLED[_id]:
                return
            await message.channel.send('\n'.join([
                '```',
                f'@sensei stoptimer \'id\': \'{_id}\'',
                '```',
                f'{arg.repeat}回のインターバルが完了しました。',
                f'お疲れさまでした！',
            ]))

@commands
class StartTimerMin(StartTimerSec):
    def __init__(self):
        super().__init__()
        self.unit_int = 60
        self.unit_str = '分'
        self.example = dotdict({'countdown':0, 'study':1, 'rest':1, 'repeat':2})
        self.arg_comment = dotdict({'countdown':f'開始までの{self.unit_str}数', 'study':f'勉強する{self.unit_str}数', 'rest':f'休憩する{self.unit_str}数', 'repeat':'繰り返しの回数'})
        self.func_comment = [
            '勉強＆休憩の繰り返しをタイマーが通知して支援してくれるコマンドです。',
            f'極端な値の入力は弾かれる場合があります。',
        ]

@commands
class StopTimer(BaseRunner):
    def __init__(self):
        super().__init__()
        self.example = dotdict({'id': '2bb8638717f17e44a3726afd245445c2'})
        self.arg_comment = dotdict({'id': '停止したいタイマーid'})
        self.func_comment = [
            '必要がなくなったタイマーを停止するコマンドです。',
        ]

    def check(self, arg: dotdict) -> bool:
        if not 'id' in arg: return False
        if not type(arg.id) == str: return False
        return True

    async def run(
        self,
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
            f'を停止しました',
        ]))

@commands
class Share(BaseRunner):
    def __init__(self):
        super().__init__()
        self.example = dotdict({})
        self.arg_comment = dotdict({'なし': '引数は要りません'})
        self.func_comment = [
            '勉強に活用する共有URLを教えてくれるコマンドです。'
        ]

    async def run(
        self,
        message: Message,
        arg: dotdict,
        ) -> None:
        await message.channel.send('\n'.join([
            '共有URLはこちらです！',
            SHARE_URL,
        ]))


@commands
class GUITimer(BaseRunner):
    def __init__(self):
        super().__init__()
        self.func_comment = [ 'ボタンを押して操作するタイマーです。', ]

    async def run(self, message: Message, arg: dotdict) -> None:
        global TIMERSTATES
        _id = myhash(message)
        # %%
        json = { "content": "勉強時間(秒)", "components": [ { "type": 1, "components": [ {
            "type": 3,
            "custom_id": f"menu_study_{_id}",
            "options":[{"label":f"{i}秒", "value":i} for i in map(str, range(5, 65, 5))],
        }, ] } ] }
        normal_url = returnNormalUrl(message.channel.id)
        r = requests.post(normal_url, headers=HEADERS, json=json)
        pprint(r)
        json = { "content": "休憩時間(秒)", "components": [ { "type": 1, "components": [ {
            "type": 3,
            "custom_id": f"menu_rest_{_id}",
            "options":[{"label":f"{i}秒", "value":i} for i in map(str, range(5, 65, 5))],
        }, ] } ] }
        normal_url = returnNormalUrl(message.channel.id)
        r = requests.post(normal_url, headers=HEADERS, json=json)
        pprint(r)
        json = { "content": "繰り返し回数", "components": [ { "type": 1, "components": [ {
            "type": 3,
            "custom_id": f"menu_repeat_{_id}",
            "options":[{"label":f"{i}回", "value":i} for i in map(str, range(1, 11))],
        }, ] } ] }
        normal_url = returnNormalUrl(message.channel.id)
        r = requests.post(normal_url, headers=HEADERS, json=json)
        pprint(r)
        json = { "content": "タイマースタート", "components": [ { "type": 1, "components": [ {
            "type": 2,
            "label": "Start Timer",
            "style": 3,
            "custom_id": f"menu_start_{_id}",
        }, ] } ] }
        normal_url = returnNormalUrl(message.channel.id)
        r = requests.post(normal_url, headers=HEADERS, json=json)
        pprint(r)
        while not TIMERSTATES[_id].start:
            await asyncio.sleep(1)
        await message.channel.send('\n'.join([
            f"{TIMERSTATES[_id]}",
        ]))
        # %%

        runner = StartTimerSec()
        arg = dotdict(
            study  = TIMERSTATES[_id].study,
            rest   = TIMERSTATES[_id].rest,
            repeat = TIMERSTATES[_id].repeat,
            countdown = 0,
        )
        if runner.check(arg):
            await runner.run(message, arg, _id=_id)
        else:
            await runner.description(message, "starttimersec")
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game("Python")) #Pythonをプレイ中

@client.event
async def on_socket_response(message: Message):
    if message["t"] != "INTERACTION_CREATE":
        return
    custom_id = message["d"]["data"]["custom_id"]
    normal_url = returnNormalUrl(message["d"]["channel_id"])
    prefix: List[str] = custom_id.split("_")
    _id = custom_id.split("_")[-1]
    if prefix[0] == "del":
        global CANCELLED
        CANCELLED[_id] = True
        json = {
            "content": f"タイマー {_id} は削除されました。"
        }
        r = requests.post(normal_url, headers=HEADERS, json=json)
    elif prefix[0] == "menu":
        global TIMERSTATES
        if prefix[1] == "start":
            TIMERSTATES[_id].start = True
        else:
            value = message["d"]["data"]["values"][0] # 単一選択なので要素1つのリストが返る
            if prefix[1] == "rest":
                TIMERSTATES[_id].rest = int(value)
            if prefix[1] == "study":
                TIMERSTATES[_id].study = int(value)
            if prefix[1] == "repeat":
                TIMERSTATES[_id].repeat = int(value)
            json = { "content": f"[DEBUG]: {value}, {custom_id}" }
            r = requests.post(normal_url, headers=HEADERS, json=json)
    await notify_callback(message["d"]["id"], message["d"]["token"])

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
        runner = commands[command]()
        arg = parse2dotdict(content)
        if runner.check(arg):
            await runner.run(message, arg)
        else:
            await runner.description(message, command)
    else:
        if len(contents) > 0 and contents[0] == "helpall":
            await message.channel.send('\n'.join([
                commands[command]()._description(message, command)
                for command in commands
            ]))
        else:
            await message.channel.send('\n'.join(
            [
                f"**{command}** コマンド: {' '.join(commands[command]().func_comment)}"
                for command in commands
            ]+[
                '詳細を表示するには以下を実行してください。',
                '```',
                '@sensei helpall',
                '```',
                '特定のコマンドの詳細を表示するには以下を実行してください。',
                '```',
                '@sensei コマンド名　help',
                '```',
            ]))

def main():
    client.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()