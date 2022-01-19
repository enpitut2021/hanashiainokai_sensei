from .BaseRunner import BaseRunner
import os
from dotdict import dotdict

from senseibot.utils import returnNormalUrl
from .BaseRunner import BaseRunner
from senseibot.logger import logger
from senseibot.utils import send_text
from dotenv import load_dotenv

load_dotenv()
SHARE_URL = os.environ["SHARE_URL"]
class Share(BaseRunner):
    def check(self, arg: dotdict) -> bool:
        pass

    async def run(self, args=None):
        msg = "\n".join(
            [
                "共有URLはこちらです！",
                SHARE_URL,
            ]
        )
        await send_text(msg, self.client, self.channel_id)

    @property
    def func_comment(self) -> list:
        comment = ["勉強に活用する共有URLを教えてくれるコマンドです。"]
        return comment

    @property
    def arg_comment(self) -> dotdict():
        comments = dotdict({"なし": "引数は要りません"})
        return comments
