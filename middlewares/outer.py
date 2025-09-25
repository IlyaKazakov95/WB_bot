from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import TelegramObject, User
from config.config import Database
import datetime as dt

class OuterMiddleware(BaseMiddleware):
    def __init__(self):
        self.user_dict = {}
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
        ) -> Any:
        data["user_dict"] = self.user_dict
        user: User = data.get("event_from_user")
        if user.id not in data["user_dict"]:
            new_user = Database(username=f'{user.first_name} {user.last_name}',
                                requests_qty=1,
                                last_requests_date=str(dt.datetime.now()))
            data["user_dict"][user.id] = new_user
        else:
            data["user_dict"][user.id].requests_qty += 1
            data["user_dict"][user.id].last_requests_date = str(dt.datetime.now())
        result = await handler(event, data)
        return result
