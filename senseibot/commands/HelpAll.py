from .BaseRunner import BaseRunner
import os
from dotdict import dotdict

from senseibot.utils import all_subclasses, returnNormalUrl
from .BaseRunner import BaseRunner
from senseibot.logger import logger
from senseibot.utils import send_text

class HelpAll(BaseRunner):

    def check(self, arg: dotdict) -> bool:
        pass

    async def run(self, arg=None):
        all_commands = all_subclasses(BaseRunner)

        msg = "\n".join(
            [
                f"**{command}**: {' '.join(all_commands[command](self.client, self.channel_id).func_comment)}"
                for command in all_commands
            ]
            + [
                "詳細を表示するには以下を実行してください。",
                "```",
                "@sensei helpall",
                "```",
                "特定のコマンドの詳細を表示するには以下を実行してください。",
                "```",
                "@sensei コマンド名　help",
                "```",
            ]
        )

        await send_text(msg, self.client, self.channel_id)

    @property
    def func_comment(self) -> list:
        comment = ["このコマンドを実行すると、全部のコマンドのヘルプを表示します。"]
        return comment

    @property
    def arg_comment(self) -> dotdict():
        comments = dotdict({"なし": "引数は要りません"})
        return comments
