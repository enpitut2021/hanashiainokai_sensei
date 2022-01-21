import asyncio
from senseibot.logger import logger, set_log_level
from .BaseRunner import BaseRunner
from ..utils import all_subclasses, myhash, send_text, notify_callback
from dotdict import dotdict
import os

from senseibot.utils import returnNormalUrl
import requests
from senseibot.commands.Timer import TIMERSTATES

all_commands = all_subclasses(BaseRunner)


class GUITimer(BaseRunner):
    def check(self):
        pass
    
    async def run(self, arg=None) -> None:
        global TIMERSTATES
        DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
        HEADERS = {"Authorization": f"Bot {DISCORD_TOKEN}"}

        channel_id = self.channel_id
        client = self.client

        _id = myhash(channel_id)
        logger.debug(f"id: {_id}")

        def send_gui_button(custom_id, options, content, component_type=3):
            print(f"custom_id: {custom_id}, type={type(custom_id)}")
            print(f"options: {options}, type={type(options)}")
            print(f"content: {content}, type={type(content)}")
            
            json = {
                "content": content,
                "components": [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": component_type,
                                "custom_id": custom_id,
                                "options": options,
                            },
                        ],
                    }
                ],
            }

            normal_url = returnNormalUrl(channel_id)
            rq = requests.post(normal_url, headers=HEADERS, json=json)
            logger.info(f"GUI `{content}` sent with {rq.status_code}")

        # ボタンで使用するコマンドを指定
        command = "starttimermin"
        runner = all_commands[command](self.client, self.channel_id)

        # 勉強時間を設定するGUIを表示
        unit = runner.unit_str
        content = f"勉強時間({unit})"
        custom_id = f"guitimer_study_{_id}"
        options = [
            {"label": f"{i}{unit}", "value": i} for i in map(str, [1] + list(range(5, 65, 5)))
        ]

        send_gui_button(custom_id, options, content)

        # 休憩時間を設定するGUIを表示
        content = f"休憩時間({unit})"
        custom_id = f"guitimer_rest_{_id}"
        options = [
            {"label": f"{i}{unit}", "value": i} for i in map(str, [1] + list(range(5, 65, 5)))
        ]
        send_gui_button(custom_id, options, content)

        # 繰り返し回数を設定するGUIを表示
        content = f"繰り返し回数"
        custom_id = f"guitimer_repeat_{_id}"
        options = [{"label": f"{i}回", "value": i} for i in map(str, range(1, 11))]
        send_gui_button(custom_id, options, content)

        # タイマーを開始するボタンを表示
        json = {
            "content": "タイマースタート",
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "label": "Start Timer",
                            "style": 3,
                            "custom_id": f"guitimer_start_{_id}",
                        },
                    ],
                }
            ],
        }
        normal_url = returnNormalUrl(channel_id)
        rq = requests.post(normal_url, headers=HEADERS, json=json)
        logger.info(f"Button `タイマースタート` sent with {rq.status_code}")
        
        
    # async def start(self, _id):
    #     channel_id = self.channel_id
    #     client = self.client
    #     TIMERSTATES[_id].start = True

    #     msg = "\n".join(
    #         [
    #             f"勉強時間{TIMERSTATES[_id].study}分、休憩時間{TIMERSTATES[_id].rest}分、繰り返し{TIMERSTATES[_id].repeat}回でタイマーを開始します。",
    #         ]
    #     )

    #     await send_text(msg, client, channel_id)

    #     arg = dotdict(
    #         study=TIMERSTATES[_id].study,
    #         rest=TIMERSTATES[_id].rest,
    #         repeat=TIMERSTATES[_id].repeat,
    #         countdown=0,
    #     )

    #     command = "starttimermin"
    #     runner = all_commands[command](self.client, self.channel_id)

    #     if runner.check(arg):
    #         await runner.run(arg, _id=_id)
    #     else:
    #         await runner.description(command)
        

    @property
    def func_comment(self) -> list:
        comment = ["ボタンを押して操作するタイマーです。"]
        return comment

    @property
    def arg_comment(self) -> dotdict():
        comments = dotdict({"なし": "引数は要りません"})
        return comments

        # json = {
        #     "content": "繰り返し回数",
        #     "components": [
        #         {
        #             "type": 1,
        #             "components": [
        #                 {
        #                     "type": 3,
        #                     "custom_id": f"menu_repeat_{_id}",
        #                     "options": [
        #                         {"label": f"{i}回", "value": i}
        #                         for i in map(str, range(1, 11))
        #                     ],
        #                 },
        #             ],
        #         }
        #     ],
        # }

        # json = {
        #     "content": f"休憩時間({u})",
        #     "components": [
        #         {
        #             "type": 1,
        #             "components": [
        #                 {
        #                     "type": 3,
        #                     "custom_id": f"menu_rest_{_id}",
        #                     "options": [
        #                         {"label": f"{i}{u}", "value": i}
        #                         for i in map(str, range(5, 65, 5))
        #                     ],
        #                 },
        #             ],
        #         }
        #     ],
        # }
        # json = {
        #     "content": f"勉強時間({u})",
        #     "components": [
        #         {
        #             "type": 1,
        #             "components": [
        #                 {
        #                     "type": 3,
        #                     "custom_id": f"menu_study_{_id}",
        #                     "options": [
        #                         {"label": f"{i}{u}", "value": i}
        #                         for i in map(str, range(5, 65, 5))
        #                     ],
        #                 },
        #             ],
        #         }
        #     ],
        # }

        # normal_url = returnNormalUrl(channel_id)
        # r = requests.post(normal_url, headers=HEADERS, json=json)
        # logger.debug(r)

        # json = {
        #     "content": f"休憩時間({u})",
        #     "components": [
        #         {
        #             "type": 1,
        #             "components": [
        #                 {
        #                     "type": 3,
        #                     "custom_id": f"menu_rest_{_id}",
        #                     "options": [
        #                         {"label": f"{i}{u}", "value": i}
        #                         for i in map(str, range(5, 65, 5))
        #                     ],
        #                 },
        #             ],
        #         }
        #     ],
        # }

        # r = requests.post(normal_url, headers=HEADERS, json=json)
        # logger.debug(r)
        # json = {
        #     "content": "繰り返し回数",
        #     "components": [
        #         {
        #             "type": 1,
        #             "components": [
        #                 {
        #                     "type": 3,
        #                     "custom_id": f"menu_repeat_{_id}",
        #                     "options": [
        #                         {"label": f"{i}回", "value": i}
        #                         for i in map(str, range(1, 11))
        #                     ],
        #                 },
        #             ],
        #         }
        #     ],
        # }

        # r = requests.post(normal_url, headers=HEADERS, json=json)
        # logger.debug(r)
        # json = {
        #     "content": "タイマースタート",
        #     "components": [
        #         {
        #             "type": 1,
        #             "components": [
        #                 {
        #                     "type": 2,
        #                     "label": "Start Timer",
        #                     "style": 3,
        #                     "custom_id": f"menu_start_{_id}",
        #                 },
        #             ],
        #         }
        #     ],
        # }

        # r = requests.post(normal_url, headers=HEADERS, json=json)
        # logger.debug(r)

