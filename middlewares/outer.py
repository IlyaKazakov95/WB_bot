from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import TelegramObject, User
from config.config import Database
import datetime as dt
from redis.asyncio import Redis
from dataclasses import asdict
import json
import logging

logger = logging.getLogger(__name__)

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
        logger.debug("OuterMiddleware запущена")
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        key = f"user:{user_id}"
        user_json = await self.redis.get(key)
        if user_json:
            user_data = json.loads(user_json)
            user_data["requests_qty"] += 1
            user_data["last_requests_date"] = str(dt.datetime.now())
            logger.info(f"Обновлены данные пользователя {user.id} ({user.first_name} {user.last_name}): "
                        f"requests_qty={user_data['requests_qty']}")
        else:
            user_data = asdict(Database(
                username=f"{user.first_name} {user.last_name}",
                requests_qty=1,
                last_requests_date=str(dt.datetime.now())
            ))
            logger.info(f"Обновлены данные пользователя {user.id} ({user.first_name} {user.last_name}): "
                        f"requests_qty={user_data['requests_qty']}")
        await self.redis.set(key, json.dumps(user_data), ex=86400 * 360)
        data["redis"] = self.redis
        return await handler(event, data)
