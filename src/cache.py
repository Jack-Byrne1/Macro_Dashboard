from functools import lru_cache

@lru_cache(maxsize=64)
def memoize_df(key: str, fetch_fn, *args, **kwargs):
    return fetch_fn(*args, **kwargs)
