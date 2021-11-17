import discord
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
client = discord.Client()

"""
勉強会を通知するメッセージの message_id がどれを指すものかを判定する必要がある
勉強会ごとにroleが定まっている。（無いならroleを作成する）
勉強会メッセージにリアクションした人にroleを付与する

scrape.py: Djangoから勉強会をスクレイピングしてmessageをdiscord内に送る
^
| データ共有す
v
notify.py: リアクションに従ってrole(教室1,2…)を付与する
"""


@client.event
async def on_raw_reaction_add(payload):
#    if payload.message_id == ID:
    if True:
        user_id = payload.user_id
        print(payload.emoji.name)
#        guild_id = payload.guild_id
#        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
#
#        role = discord.utils.find(lambda r: r.name == payload.emoji.name, guild.roles)
#
#        if role is not None:
#            print(role.name + " was found!")
#            print(role.id)
#            member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
#            await member.add_roles(role)
#            print("done")
#

@client.event
async def on_raw_reaction_remove(payload):
    pass

@client.event
async def on_ready():
    print("Botは正常に起動しました！")
    print(client.user.name)  # ボットの名前
    print(client.user.id)  # ボットのID
    print(discord.__version__)  # discord.pyのバージョン
    print('------')
    await client.change_presence(activity=discord.Game(name="役職を管理！"))


client.run(DISCORD_TOKEN)