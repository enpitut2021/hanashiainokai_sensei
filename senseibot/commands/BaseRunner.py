from abc import ABC, abstractmethod, abstractproperty
from dotdict import dotdict

from senseibot.utils import send_text


class BaseRunner(ABC):
    def __init__(self, client, channel_id):
        self.func_name = self.__class__.__name__.lower()
        self.client = client
        self.channel_id = channel_id

    def _description(self) -> str:
        return "\n".join(
            [f"**{self.func_name} コマンドの説明**"]
            + [f"> {txt}" for txt in self.func_comment]
            + ["引数の説明"]
            + [f"    `'{arg}'`: {self.arg_comment[arg]}" for arg in self.arg_comment]
            + [f"実行例"]
            + [
                "```",
                f"@sensei {self.func_name} {str(self.example)[1:][:-1]}",
                "```",
            ]
        )

    async def description(self) -> None:
        if self.func_comment == []:
            return
        await send_text(self._description(), self.channel_id)

    @abstractmethod
    def check(self, arg: dotdict) -> bool:
        pass

    @abstractmethod
    async def run(self) -> None:
        pass

    @abstractproperty
    def func_comment(self) -> list:
        pass

    @abstractproperty
    def arg_comment(self) -> dotdict():
        pass

        # self.example: dotdict = dotdict()

all_commands = BaseRunner.__subclasses__()
