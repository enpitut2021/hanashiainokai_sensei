import requests, json
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os
import datetime
#from collections import defaultdict

load_dotenv()
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
HEADERS = { "Authorization": f"Bot {DISCORD_TOKEN}" }
SHARE_URL = os.environ['SHARE_URL']

#CANCELLED: DefaultDict[str, bool] = defaultdict(bool)
CHANNEL_ID=870493181555400714

client = discord.Client()






# start = calendar['start_time']

@tasks.loop(seconds=30)
async def loop():
    # botが起動するまで待つ
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    url = requests.get("https://hanashiainokairegistration.herokuapp.com/tobot/2021/12/8/")
    text = url.text


    dt_now = datetime.datetime.now()

    data = json.loads(text)

    month=str(dt_now.month).zfill(2)
    day=str(dt_now.day).zfill(2)
    schedule = data[f"{dt_now.year}.{month}.{day}"] 
    for i in range (len(schedule)):
        schedule_dict = schedule[i]
        print(schedule_dict["summary"])
        await channel.send(f"""{month}/{day} {schedule_dict["start_time"]}~{schedule_dict["end_time"]} {schedule_dict["summary"]}""")

#ループ処理実行
loop.start()
# Botの起動とDiscordサーバーへの接続
client.run(DISCORD_TOKEN)

#print(start)