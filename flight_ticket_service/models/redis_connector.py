import json

from redis.asyncio import Redis

redis = Redis(host='localhost', port=6380, decode_responses=True)


async def set_cache(key, data, redis_client):
    await redis_client.set(key, json.dumps(data), ex=600)


async def get_cache(key, redis_client):
    cached_data = await redis_client.get(key)
    if cached_data is not None:
        return json.loads(cached_data)
    return None

