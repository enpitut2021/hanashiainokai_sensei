import asyncio
import dataclasses
import os
from collections import defaultdict
from xmlrpc import client

import requests
from dotdict import dotdict
from senseibot.utils import myhash, returnNormalUrl, send_text

from .BaseRunner import BaseRunner


@dataclasses.dataclass
class TimerState:
    study: int = 25
    rest: int = 5
    repeat: int = 3
    start: bool = False


TIMERSTATES = defaultdict(TimerState)
CANCELLED = defaultdict(bool)
REPEAT_MAX = 10
STUDY_MAX = 24 * 60 * 60
REST_MAX = 24 * 60 * 60


class StartTimerSec(BaseRunner):
    def __init__(self, client, channel_id):
        super().__init__(client, channel_id)
        self.unit_int = 1
        self.unit_str = "秒"
        self.example = dotdict({"countdown": 0, "study": 1, "rest": 1, "repeat": 2})

    def check(self, arg: dotdict) -> bool:
        if not "countdown" in arg:
            return False
        if not "study" in arg:
            return False
        if not "rest" in arg:
            return False
        if not "repeat" in arg:
            return False
        if not type(arg.countdown) == int:
            return False
        if not type(arg.study) == int:
            return False
        if not type(arg.rest) == int:
            return False
        if not type(arg.repeat) == int:
            return False
        if not self.unit_int * arg.study in range(STUDY_MAX):
            return False
        if not self.unit_int * arg.rest in range(REST_MAX):
            return False
        if not arg.repeat in range(REPEAT_MAX):
            return False
        return True

    async def run(
        self,
        _id,
    ):
        channel_id = self.channel_id
        client = self.client
        
        global CANCELLED
        global TIMERSTATES
        
        DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
        HEADERS = {"Authorization": f"Bot {DISCORD_TOKEN}"}

        msg = "\n".join(
            [
                f"勉強時間{TIMERSTATES[_id].study}分、休憩時間{TIMERSTATES[_id].rest}分、繰り返し{TIMERSTATES[_id].repeat}回でタイマーを開始します。",
            ]
        )
        await send_text(msg, client, channel_id)

        arg = dotdict(
            study=TIMERSTATES[_id].study,
            rest=TIMERSTATES[_id].rest,
            repeat=TIMERSTATES[_id].repeat,
            countdown=0,
        )

        normal_url = returnNormalUrl(channel_id)
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
                            "custom_id": f"guitimer_del_{_id}",
                        },
                    ],
                }
            ],
        }
        r = requests.post(normal_url, headers=HEADERS, json=json)
        
        # TODO requests.postの合否判定が必要か？
        await asyncio.sleep(arg.countdown * self.unit_int)
        for i in range(1, arg.repeat + 1):
            if CANCELLED[_id]:
                break
            msg = "\n".join(
                    [
                        f"{i}/{arg.repeat}回目の勉強時間になりました。",
                        f"勉強を{arg.study}{self.unit_str}はじめてください。",
                    ]
                )
            await send_text(msg, self.client, self.channel_id)
            
            await asyncio.sleep(arg.study * self.unit_int)
            if CANCELLED[_id]:
                break
            if i == arg.repeat:
                continue
            msg = "\n".join(
                    [
                        f"{i}/{arg.repeat}回目の休憩時間になりました。",
                        f"休憩を{arg.rest}{self.unit_str}とってください。",
                    ]
                )
            await send_text(msg, self.client, self.channel_id)
            await asyncio.sleep(arg.rest * self.unit_int)
        else:
            if CANCELLED[_id]:
                return
            
            msg = "\n".join(
                    [
                        f"{arg.repeat}回のインターバルが完了しました。",
                        f"お疲れさまでした！",
                    ]
                )
            await send_text(msg, self.client, self.channel_id)

    @property
    def func_comment(self) -> list:
        comment = [
            "勉強＆休憩の間隔をタイマーが通知して支援してくれるコマンドです。",
            f"極端な値の入力は弾かれる場合があります。",
        ]
        return comment

    @property
    def arg_comment(self) -> dotdict():
        comments = dotdict(
            {
                "countdown": f"開始までの{self.unit_str}数",
                "study": f"勉強する{self.unit_str}数",
                "rest": f"休憩する{self.unit_str}数",
                "repeat": "インターバルの回数",
            }
        )
        return comments


class StartTimerMin(StartTimerSec):
    def __init__(self, client, channel_id):
        super().__init__(client, channel_id)
        self.unit_int = 60
        self.unit_str = "分"
        self.example = dotdict({"countdown": 0, "study": 1, "rest": 1, "repeat": 2})

    @property
    def func_comment(self) -> list:
        comment = [
            "勉強＆休憩の間隔をタイマーが通知して支援してくれるコマンドです。",
            f"極端な値の入力は弾かれる場合があります。",
        ]
        return comment

    @property
    def arg_comment(self) -> dotdict():
        comments = dotdict(
            {
                "countdown": f"開始までの{self.unit_str}数",
                "study": f"勉強する{self.unit_str}数",
                "rest": f"休憩する{self.unit_str}数",
                "repeat": "繰り返しの回数",
            }
        )
        return comments


class StopTimer(BaseRunner):
    def __init__(self):
        super().__init__()
        self.example = dotdict({"id": "2bb8638717f17e44a3726afd245445c2"})
        self.arg_comment = dotdict({"id": "停止したいタイマーid"})
        self.func_comment = [
            "必要がなくなったタイマーを停止するコマンドです。",
        ]

    def check(self, arg: dotdict) -> bool:
        if not "id" in arg:
            return False
        if not type(arg.id) == str:
            return False
        return True

    async def run(
        self,
        arg: dotdict,
    ) -> None:
        global CANCELLED
        _id = arg.id
        CANCELLED[_id] = True
        await message.channel.send(
            "\n".join(
                [
                    "```",
                    f"'id': '{_id}'",
                    "```",
                    f"を停止しました",
                ]
            )
        )
