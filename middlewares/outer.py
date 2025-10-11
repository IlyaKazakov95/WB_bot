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
        user: User | None = None

        # пытаемся достать пользователя из события
        if hasattr(event, "from_user"):
            user = event.from_user
        elif "event_from_user" in data:
            user = data["event_from_user"]

        if not user:
            logger.debug("⛔ Middleware: событие без пользователя, пропускаем.")
            return await handler(event, data)

        user_id = user.id
        key = f"user:{user_id}"

        try:
            user_json = await self.redis.get(key)
            if user_json:
                user_data = json.loads(user_json)
                user_data["requests_qty"] += 1
                user_data["last_requests_date"] = str(dt.datetime.now())
                logger.info(f"🔄 Обновлены данные пользователя {user_id} ({user.username})")
            else:
                user_data = asdict(Database(
                    username=f"{user.first_name or ''} {user.last_name or ''}".strip(),
                    requests_qty=1,
                    last_requests_date=str(dt.datetime.now())
                ))
                logger.info(f"🆕 Новый пользователь: {user_id} ({user.username})")

            await self.redis.set(key, json.dumps(user_data), ex=86400 * 30)
            data["user_dict"] = user_data

        except Exception as e:
            logger.exception(f"❌ Ошибка в OuterMiddleware для user_id={user_id}: {e}")

        return await handler(event, data)
