from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from config.config import Database
import datetime as dt

user_dict = {}

class OuterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
        ) -> Any:
        user: User = data.get("event_from_user")
        if user.id not in user_dict:
            new_user = Database(username=f'{user.first_name} {user.last_name}',
                                requests_qty=0,
                                last_requests_date=str(dt.datetime.now()))
            user_dict[user.id] = new_user
        else:
            user_dict[user.id].requests_qty += 1
            user_dict[user.id].last_requests_date = str(dt.datetime.now())
        result = await handler(event, data)
        return result
