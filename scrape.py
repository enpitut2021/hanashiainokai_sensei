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
# channelIDを シケタイ/作業会予約＆通知 から取ってくる
# https://qiita.com/Eai/items/1165d08dce9f183eac74