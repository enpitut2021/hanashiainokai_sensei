import os
import requests
from dotdict import dotdict

from senseibot.utils import returnNormalUrl
from .BaseRunner import BaseRunner
from senseibot.logger import logger

class Summon(BaseRunner):

    def check(self, arg: dotdict) -> bool:
        pass

    async def run(self, args=None):
        DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
        HEADERS = {"Authorization": f"Bot {DISCORD_TOKEN}"}

        components = []
        button_commands = ["share", "calendar", "guitimer", "helpall"]
        for command in button_commands:
            components.append(
                {
                    "type": 2,
                    "label": f"{command}",
                    "style": 3,
                    "custom_id": f"button_{command}",
                },
            )
        help_json = {
            "content": "以下のボタンで各コマンドを実行できます",
            "components": [{"type": 1, "components": components}],
        }

        rq = requests.post(
            returnNormalUrl(self.channel_id),
            headers=HEADERS,
            json=help_json,
        )
        logger.info(f"command `summon` finished with {rq.status_code}")

    @property
    def func_comment(self) -> list:
        comment = ["このコマンドを実行すると、ボタンを表示します。"]
        return comment
    
    @property
    def arg_comment(self) -> dotdict():
        pass

