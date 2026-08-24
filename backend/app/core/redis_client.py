"""
In-memory Cache (formerly Redis wrapper).

Used for:
  1. Caching expensive route-finder responses (external Directions API calls)
  2. Refresh-token / logout blacklisting
  3. Simple per-user rate limiting

The rest of the app should depend on `get_cache()` (see api/deps.py) rather
than importing this module's `cache` directly.
"""
import time
from typing import Any, Optional

class RedisCache:
    def __init__(self):
        self._store = {}

    async def get_json(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if item is None:
            return None
        value, expiry = item
        if expiry and time.time() > expiry:
            del self._store[key]
            return None
        return value

    async def set_json(self, key: str, value: Any, ttl: int = 300) -> None:
        self._store[key] = (value, time.time() + ttl)

    async def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]

    async def add_to_blacklist(self, jti: str, ttl_seconds: int) -> None:
        self._store[f"blacklist:{jti}"] = ("1", time.time() + ttl_seconds)

    async def is_blacklisted(self, jti: str) -> bool:
        key = f"blacklist:{jti}"
        item = self._store.get(key)
        if item is None:
            return False
        _, expiry = item
        if expiry and time.time() > expiry:
            del self._store[key]
            return False
        return True

    async def incr_with_expiry(self, key: str, ttl_seconds: int) -> int:
        item = self._store.get(key)
        current_time = time.time()
        
        if item is None or (item[1] and current_time > item[1]):
            self._store[key] = (1, current_time + ttl_seconds)
            return 1
            
        count, expiry = item
        self._store[key] = (count + 1, expiry)
        return count + 1

    async def ping(self) -> bool:
        return True

cache = RedisCache()
