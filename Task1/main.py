import functools
import time
from collections import OrderedDict
import requests
import tracemalloc


def memory(func):
    @functools.wraps(func)
    def wrapper_memory(*args, **kwargs):
        tracemalloc.start()
        start_snapshot = tracemalloc.take_snapshot()
        value = func(*args, **kwargs)
        finish_snapshot = tracemalloc.take_snapshot()
        top_stats = start_snapshot.compare_to(finish_snapshot, 'lineno')
        print(f'Used memory: {top_stats.__sizeof__() / 1024} Mb')
        return value
    return wrapper_memory


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Time to finish {func.__name__!r} in {run_time:.4f} secs")
        return value

    return wrapper_timer


def cache(_func=None, *, max_limit=2):
    def internal(func):
        @functools.wraps(func)
        def deco(*args, **kwargs):
            cache_key = (args, tuple(kwargs.items()))
            if cache_key in deco.cache:
                deco.cache.move_to_end(cache_key, last=False)
                return deco.cache[cache_key]
            result = func(*args, **kwargs)
            if len(deco.cache) >= max_limit:
                deco.cache.popitem(last=True)
            deco.cache[cache_key] = result
            return result

        deco.cache = OrderedDict()
        return deco

    if _func is None:
        return internal
    else:
        return internal(_func)


@memory
@timer
@cache
def fetch_url(_url):
    return requests.get(_url)


urls = ['https://google.com', 'https://google.com', 'https://youtube.com', 'https://youtube.com', 'https://google.com',
        'https://www.gov.uk', 'https://google.com', 'https://ithillel.ua', 'https://google.com', 'https://youtube.com']
first_n = 100
for url in urls:
    res = fetch_url(url)
    print(res.content[:first_n] if first_n else res.content)
