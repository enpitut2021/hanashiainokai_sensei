import os
import discord
from dotenv import load_dotenv
from datetime import datetime
import time
import ast
from typing import *
from dotdict import dotdict

load_dotenv()
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

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

def check_timer_arg(arg: dotdict) -> bool:
    """
    timer コマンドの引数が正しいか 返す関数
    """
    if not 'countdown_sec' in arg: return False
    if not 'study_sec'     in arg: return False
    if not 'break_sec'     in arg: return False
    if not 'interval_num'  in arg: return False
    if not type(arg.countdown_sec) == int: return False
    if not type(arg.study_sec)     == int: return False
    if not type(arg.break_sec)     == int: return False
    if not type(arg.interval_num)  == int: return False
    return True

async def mysleep(t: int) -> None:
    for _ in range(t):
        time.sleep(1)

@client.event
async def on_message(message):
    # 自分自身のメッセージは無視する
    if message.author == client.user:
        return

    # sensei から始まらないメッセージは無視する
    content = message.content
    if not content.startswith('sensei '):
        return
    content = message.content[len('sensei '):]
    # 以降message.contentを使わずcontentを使って処理を書く

    # test用のコマンド， 新しい処理はここで試す
    command = 'test'
    if content.startswith(command):
        arg = parse2dotdict(command, content)
        await message.channel.send(str(arg))

    command = 'timer'
    if content.startswith(command):
        usage = """
        sensei timer 'countdown_sec':60, 'study_sec':3600, 'break_sec':600, 'interval_num':2
        """.strip()
        arg = parse2dotdict(command, content)
        if check_timer_arg(arg):
            await message.channel.send('\n'.join([
                f'{arg.countdown_sec}秒後にタイマーをセットしました。',
                f'設定は、',
                f'勉強時間が{arg.study_sec}秒',
                f'休憩時間が{arg.break_sec}秒',
                f'回数が{arg.interval_num}回',
                f'です',
            ]))
            await mysleep(arg.countdown_sec)
            for i in range(1, arg.interval_num+1):
                await message.channel.send('\n'.join([
                    f'{i}回目の勉強時間になりました。',
                    f'勉強を{arg.study_sec}秒開始してください。',
                ]))
                await mysleep(arg.study_sec)
                await message.channel.send('\n'.join([
                    f'{i}回目の休憩時間になりました。',
                    f'休憩を{arg.break_sec}秒開始してください。',
                ]))
                await mysleep(arg.break_sec)
            await message.channel.send('\n'.join([
                f'{i}回のインターバルが完了しました。',
                f'お疲れさまでした！',
            ]))
        else:
            await message.channel.send('[USAGE] '+usage)

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
