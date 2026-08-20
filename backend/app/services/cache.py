from redis import Redis

from app.core.config import get_settings


def redis_client() -> Redis:
    return Redis.from_url(get_settings().redis_url, decode_responses=True)


def get_cache(key: str) -> str | None:
    try:
        with redis_client() as client:
            return client.get(key)
    except Exception:
        return None


def set_cache(key: str, value: str, ttl: int | None = None) -> None:
    try:
        with redis_client() as client:
            client.set(key, value, ex=ttl or get_settings().response_cache_ttl_seconds)
    except Exception:
        pass
