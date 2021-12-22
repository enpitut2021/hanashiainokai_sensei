import requests
import json
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os
import datetime
from time import sleep

from logger import logger, set_log_level

set_log_level("DEBUG")
#from collections import defaultdict

load_dotenv()
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
HEADERS = {"Authorization": f"Bot {DISCORD_TOKEN}"}
SHARE_URL = os.environ['SHARE_URL']

#CANCELLED: DefaultDict[str, bool] = defaultdict(bool)
CHANNEL_ID = 870493181555400714

client = discord.Client()

# start = calendar['start_time']


def get_json(year, month, day):
    """calendar情報を取得する

    Returns:
        その日のスケージュールを辞書のリストで返す。
        list [{
            "summary": str,
            "description" : str,
            "start_time": str,
            "end_time": str, 
            "room" :str
        } ... ]
    """
    url = requests.get(
        f"https://hanashiainokairegistration.herokuapp.com/tobot/{year}/{month}/{day}/")
    text = url.text
    logger.debug(text)
    if text is None:
        return []
    else:
        data = json.loads(text)
        schedules = data[f"{year}.{month}.{day}"]
        return schedules


def get_time():
    """今の時間を(year, month, day, hour, minute)で返す"""
    now = datetime.datetime.now()
    year = now.year  # 年 <- int
    month = now.month  # 月 <- int
    day = now.day  # 日 <- int
    hour = now.hour  # 時 <- int
    minute = now.minute  # 分 <- int
    return (year, month, day, hour, minute)

def time_equal(time1, time2):
    """時間を比較するときに使う"""
    assert len(time1) == len(time2)
    assert len(time1) == 5
    # time1 = (year, month, day, hour, minute)
    # time2 = (year, month, day, hour, minute)
    # Noneの場合は、指定なし
    # TODO: time1, time2 をNamed Tupleとかにしたいね

    ret = True
    for t1, t2 in zip(time1, time2):
        if t1 is None or t2 is None or t1 == t2:
            continue
        if t1 != t2:
            ret = False
            break

    logger.debug(f"Comparing time: {time1} , {time2} : {ret}")
    return ret
    # # 負の数の時のパッチ
    # if time1 < 0:



@tasks.loop(seconds=60)
async def check_loop():

    year, month, day, hour, minute = get_time()
    logger.debug("Starting schedule check")
    schedules = get_json(year, month, day)
    logger.debug(f"schedules found: {schedules}")
    for schedule in schedules:
        # ssはschedule start(スケジュールの開始時間)の略
        ss_year, ss_month, ss_day = year, month, day  # <- 今日なのでnowと同じ
        # <- これはschedulesのstart_timeを分割してintにしたもの
        ss_hour, ss_minute = list(map(int, schedule["start_time"].split(':')))

        # スケジュールの15分前かどうかをチェック
        pre_15= datetime.datetime(ss_year, ss_month, ss_day, ss_hour, ss_minute) - datetime.timedelta(minutes=15)
        if time_equal((year, month, day, hour, minute), (pre_15.year, pre_15.month, pre_15.day, pre_15.hour, pre_15.minute)):
            # 15分前なら送信する
            send_text(schedules)

        # スケジュールの開始時かどうかをチェック
        if time_equal((year, month, day, hour, minute), (ss_year, ss_month, ss_day, ss_hour, ss_minute)):
            # 15分前なら送信する
            send_text(schedules)

# @tasks.loop(seconds=60)
# async def loop():
#     # botが起動するまで待つ
#     await client.wait_until_ready()
#     channel = client.get_channel(CHANNEL_ID)

#     dt_now = datetime.datetime.now()

#     year = dt_now.year
#     month = str(dt_now.month).zfill(2)
#     day = str(dt_now.day).zfill(2)

#     url = requests.get(
#         f"https://hanashiainokairegistration.herokuapp.com/tobot/{year}/{month}/{day}/")
#     text = url.text

#     data = json.loads(text)
#     schedule = data[f"{year}.{month}.{day}"]
#     for i in range(len(schedule)):
#         schedule_dict = schedule[i]
#         print(schedule_dict["summary"])
#         await channel.send(f"""{month}/{day} {schedule_dict["start_time"]}~{schedule_dict["end_time"]} {schedule_dict["summary"]} 勉強部屋{schedule_dict["room"]}""")


def send_text(msg):

    logger.debug(f"Sending text {msg}")
    channel = client.get_channel(CHANNEL_ID)
    #TODOメッセージ表示をわかりやすく
    channel.send('\n'.join([
            '```',
            f'{msg}',
            '```',
            
        ]))

@tasks.loop(seconds=60)
async def morning_event():
    # ---現在の時刻を取得---
    now = get_time()
    year, month, day, hour, minute = now

    # ---8時じゃなかったら何もしない---
    if time_equal((None, None, None, 8, 0), now):
        return

    # ---8時に実行する内容---
    # 今日の勉強会のデータを取得
    schedules = get_json(year, month, day)

    # 今日の勉強会を送信する設定
    msg = schedules  # <- TODO: これを綺麗にしといて
    send_text.start(msg, now)

    # 今日の15分前と開始時の通知を設定する
    for schedule in schedules:
        # ssはSchedule Startの頭文字
        ss_year, ss_month, ss_day = year, month, day  # <- 今日なのでnowと同じ
        # <- これはschedulesのstart_timeを分割してintにしたもの
        ss_hour, ss_minute = list(map(int, schedule["start_time"].split(':')))

        # 15分前に通知を送信する設定
        msg = schedule  # <-15分前に送信する内容
        send_text.start(msg, (ss_year, ss_month, ss_day,
                        ss_hour, ss_minute - 1))  # <- 15分前に送信する

        # 開始時に通知を送信する設定
        msg = schedule  # <-開始時に送信する内容
        send_text.start(msg, (ss_year, ss_month, ss_day,
                        ss_hour, ss_minute))  # <- 開始時に送信する


# 15分ごとに登録状況をチェック


if __name__ == '__main__':

    check_loop.start()
    # Botの起動とDiscordサーバーへの接続
    client.run(DISCORD_TOKEN)

    # dt_now = datetime.datetime.now()

    # year = dt_now.year
    # month = str(dt_now.month).zfill(2)
    # day = str(dt_now.day).zfill(2)

    # # ループ処理実行
    # while True:
    #     print(datetime.datetime.now().minute)  # <- 今の時間を出力
    #     break
    #     sleep(1)  # <- 1秒まつ


# TODO　main.pyとの統合
