from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import TelegramObject, User
from config.config import Database
import datetime as dt
from redis.asyncio import Redis
from dataclasses import asdict
import json


class OuterMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis):
        super().__init__()
        self.redis = redis
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
        ) -> Any:
        user: User = data.get("event_from_user")
        user_id = user.id

        key = f"user:{user_id}"
        user_json = await self.redis.get(key)
        if user_json:
            user_data = json.loads(user_json)
            user_data["requests_qty"] += 1
            user_data["last_requests_date"] = str(dt.datetime.now())
        else:
            user_data = asdict(Database(
                username=f"{user.first_name} {user.last_name}",
                requests_qty=1,
                last_requests_date=str(dt.datetime.now())
            ))
        await self.redis.set(key, json.dumps(user_data), ex=86400 * 360)
        data["user_dict"] = user_data
        return await handler(event, data)
