"""
Optional Redis cache for D1, D10, BAV/SAV, Dasha results.
If REDIS_URL is not set, cache is a no-op.
"""
import os
import json
from typing import Any, Optional

_CACHE = None
_TTL = int(os.environ.get("CACHE_TTL_SECONDS", "86400"))  # 24h


def _get_redis():
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    url = os.environ.get("REDIS_URL")
    if not url:
        return None
    try:
        import redis
        _CACHE = redis.from_url(url, decode_responses=True)
        _CACHE.ping()
        return _CACHE
    except Exception:
        _CACHE = None
        return None


def cache_get(key: str) -> Optional[Any]:
    """Get JSON value from cache."""
    r = _get_redis()
    if not r:
        return None
    try:
        raw = r.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl: int = _TTL) -> bool:
    """Set JSON value in cache."""
    r = _get_redis()
    if not r:
        return False
    try:
        r.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception:
        return False


def cache_key_d1(chart_id: Optional[int], dob: Optional[str], tob: Optional[str], lat: Optional[float], lon: Optional[float]) -> str:
    """Cache key for D1 result."""
    if chart_id is not None:
        return f"d1:chart:{chart_id}"
    return f"d1:birth:{dob}:{tob}:{lat}:{lon}"


def cache_key_d10(chart_id: Optional[int], dob: Optional[str], tob: Optional[str], lat: Optional[float], lon: Optional[float]) -> str:
    """Cache key for D10 result."""
    if chart_id is not None:
        return f"d10:chart:{chart_id}"
    return f"d10:birth:{dob}:{tob}:{lat}:{lon}"


# Optional stats (in-memory)
_cache_hits = 0
_cache_misses = 0


class CacheManager:
    """
    Redis cache manager: charts, predictions, invalidation, stats.
    No-op when REDIS_URL is not set.
    """
    CHART_TTL = int(os.environ.get("CACHE_TTL", "3600"))
    PREDICTION_TTL = int(os.environ.get("CACHE_PREDICTION_TTL", "1800"))
    VALIDATION_REPORT_TTL = 86400

    def __init__(self, redis_url: Optional[str] = None):
        self._url = redis_url or os.environ.get("REDIS_URL")
        self._redis = None
        if self._url:
            try:
                import redis
                self._redis = redis.from_url(self._url, decode_responses=True)
                self._redis.ping()
            except Exception:
                self._redis = None

    def _get(self, key: str) -> Optional[Any]:
        if not self._redis:
            return None
        try:
            raw = self._redis.get(key)
            if raw is None:
                global _cache_misses
                _cache_misses += 1
                return None
            global _cache_hits
            _cache_hits += 1
            return json.loads(raw)
        except Exception:
            return None

    def _set(self, key: str, value: Any, ttl: int) -> bool:
        if not self._redis:
            return False
        try:
            self._redis.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception:
            return False

    def cache_chart(self, native_id: str, chart_type: str, chart_data: dict, ttl: Optional[int] = None) -> None:
        """Cache calculated chart. native_id can be chart_id."""
        key = f"chart:{native_id}:{chart_type}"
        self._set(key, chart_data, ttl or self.CHART_TTL)

    def get_cached_chart(self, native_id: str, chart_type: str) -> Optional[dict]:
        """Retrieve cached chart or None."""
        return self._get(f"chart:{native_id}:{chart_type}")

    def cache_prediction(self, native_id: str, prediction: dict, ttl: Optional[int] = None) -> None:
        """Cache prediction result."""
        key = f"prediction:{native_id}"
        self._set(key, prediction, ttl or self.PREDICTION_TTL)

    def get_cached_prediction(self, native_id: str) -> Optional[dict]:
        """Retrieve cached prediction or None."""
        return self._get(f"prediction:{native_id}")

    def invalidate_native_cache(self, native_id: str) -> None:
        """Delete all cache entries for a native (chart). Uses pattern scan."""
        if not self._redis:
            return
        try:
            pattern = f"*:{native_id}:*"
            keys = list(self._redis.scan_iter(match=pattern))
            if keys:
                self._redis.delete(*keys)
            key2 = f"prediction:{native_id}"
            self._redis.delete(key2)
        except Exception:
            pass

    def cache_validation_report(self, report_id: str, report: dict, ttl: Optional[int] = None) -> None:
        """Cache validation report."""
        self._set(f"validation:{report_id}", report, ttl or self.VALIDATION_REPORT_TTL)

    def get_cache_stats(self) -> dict:
        """Return hit/miss counts (best-effort)."""
        return {"hits": _cache_hits, "misses": _cache_misses}
