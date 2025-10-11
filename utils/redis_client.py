import redis.asyncio as redis
from config import RedisSettings

def init_redis(settings: RedisSettings):
    auth = ""
    if settings.username and settings.password:
        auth = f"{settings.username}:{settings.password}@"
    elif settings.password:
        auth = f":{settings.password}@"
    elif settings.username:
        auth = f"{settings.username}@"

    redis_url = f"redis://{auth}{settings.host}:{settings.port}/{settings.db}"
    return redis.from_url(redis_url, decode_responses=True)