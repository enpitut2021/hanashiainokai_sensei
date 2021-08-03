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
SHARE_URL = os.environ['SHARE_URL']
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
    async def description(
        self,
        message: Message,
        command: str,
        ) -> None:
        await message.channel.send('\n'.join(
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
        ]))

class StartTimerSec(BaseRunner):
    def __init__(self):
        super().__init__()
        self.unit_int = 1
        self.unit_str = '秒'
        self.example = dotdict({'countdown':60, 'study':1500, 'rest':300, 'repeat':2})
        self.arg_comment = dotdict({'countdown':f'開始までの{self.unit_str}数', 'study':f'勉強する{self.unit_str}数', 'rest':f'休憩する{self.unit_str}数', 'repeat':'インターバルの回数'})
        self.func_comment = [
            '勉強＆休憩の間隔をタイマーが通知して支援してくれるコマンドです。',
            f'極端な値の入力は弾かれる場合があります。',
        ]

    def check(self, arg: dotdict) -> bool:
        if not 'countdown' in arg: return False
        if not 'study'     in arg: return False
        if not 'rest' in arg: return False
        if not 'repeat'  in arg: return False
        if not type(arg.countdown) == int: return False
        if not type(arg.study)     == int: return False
        if not type(arg.rest) == int: return False
        if not type(arg.repeat)  == int: return False
        return True

    async def run(
        self,
        message: Message,
        arg: dotdict,
        ) -> None:
        global CANCELLED
        _id = myhash(message)
        await message.channel.send('\n'.join([
            '```',
            f'\'id\': \'{_id}\'',
            '```',
            f'{arg.countdown}{self.unit_str}後にタイマーをセットしました。',
            f'設定は、',
            f'勉強時間が{arg.study}{self.unit_str}',
            f'休憩時間が{arg.rest}{self.unit_str}',
            f'回数が{arg.repeat}回',
            f'です',
        ]))
        await asyncio.sleep(arg.countdown*self.unit_int)
        for i in range(1, arg.repeat+1):
            if CANCELLED[_id]:
                break
            await message.channel.send('\n'.join([
                '```',
                f'\'id\': \'{_id}\'',
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
                f'\'id\': \'{_id}\'',
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
                f'\'id\': \'{_id}\'',
                '```',
                f'{arg.repeat}回のインターバルが完了しました。',
                f'お疲れさまでした！',
            ]))

class StartTimerMin(StartTimerSec):
    def __init__(self):
        super().__init__()
        self.unit_int = 60
        self.unit_str = '分'
        self.example = dotdict({'countdown':1, 'study':25, 'rest':5, 'repeat':2})
        self.arg_comment = dotdict({'countdown':f'開始までの{self.unit_str}数', 'study':f'勉強する{self.unit_str}数', 'rest':f'休憩する{self.unit_str}数', 'repeat':'繰り返しの回数'})
        self.func_comment = [
            '勉強＆休憩の繰り返しをタイマーが通知して支援してくれるコマンドです。',
            f'極端な値の入力は弾かれる場合があります。',
        ]

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

class Nokori(BaseRunner):
    def __init__(self):
        super().__init__()
        self.example = dotdict({'time': '23:59'})
        self.arg_comment = dotdict({'time': '時:分'})
        self.func_comment = [
            '指定した時間まで残りの分数, 秒数,を教えてくれるコマンドです。',
        ]

    def check(self, arg: dotdict) -> bool:
        if not 'time' in arg: return False
        if not type(arg.time) == str: return False
        try:
            h, m = map(int, arg.time.split(':'))
        except:
            return False
        if not h in range(24):
            return False
        if not m in range(60):
            return False
        return True

    async def run(
        self,
        message: Message,
        arg: dotdict,
        ) -> None:
        hour, minute = map(int, arg.time.split(':'))
        second = 0
        now = datetime.now()
        dst =     second+60*    minute+    hour*60*60
        src = now.second+60*now.minute+now.hour*60*60
        ans = dst-src
        if ans < 0:
            ans += 24*60*60
        await message.channel.send('\n'.join([
            f'{arg.time}まで',
            f'分にして`{ans//60}`分',
            f'秒にして`{ans}`秒',
            'です。',
        ]))

class Pomodoro(StartTimerMin):
    def __init__(self):
        super().__init__()
        self.example = dotdict({'repeat':4})
        self.arg_comment = dotdict({'repeat':'インターバルの回数'})
        self.overwrite_arg  = dotdict({'countdown':0, 'study':25, 'rest':5})
        self.func_comment = [
            '「ポマドーロテクニック」25分間の勉強,5分間の休憩をrepeat回繰り返すコマンドです。',
        ]

    def check(self, arg: dotdict) -> bool:
        for k in self.overwrite_arg:
            arg[k] = self.overwrite_arg[k]
        return super().check(arg)


commands = {
    'starttimer': StartTimerMin,
#    'starttimersec': StartTimerSec,
    'stoptimer': StopTimer,
    'pomodoro': Pomodoro,
    'nokori': Nokori,
    'share': Share,
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
        runner = commands[command]()
        arg = parse2dotdict(content)
        if runner.check(arg):
            await runner.run(message, arg)
        else:
            await runner.description(message, command)
    else:
        if len(contents) > 0 and contents[0] == "helpall":
            for command in commands:
                runner = commands[command]()
                await runner.description(message, command)
        else:
            for command in commands:
                runner = commands[command]()
                await message.channel.send(f"**{command}** コマンド: {' '.join(runner.func_comment)}")
            await message.channel.send('\n'.join([
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
