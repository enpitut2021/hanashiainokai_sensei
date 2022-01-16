from dotdict import dotdict
from .BaseRunner import BaseRunner
from senseibot.utils import send_text


class Calendar(BaseRunner):
    def check(self, arg: dotdict) -> bool:
        pass

    async def run(self, args=None):
        msg = "\n".join(
            [
                "カレンダーのURLはこちらです！",
                "https://hanashiainokairegistration.herokuapp.com/calendar",
            ]
        )
        await send_text(msg, self.client, self.channel_id)

    @property
    def func_comment(self) -> list:
        comment = ["作業会予約カレンダーのURLを教えてくれるコマンドです。"]
        return comment

    @property
    def arg_comment(self) -> dotdict():
        comments = dotdict({"なし": "引数は要りません"})
        return comments
