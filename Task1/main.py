import functools
import heapq
import time
from collections import Counter
from operator import itemgetter
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


def cache_deco(_func, max_limit=2):
    def internal(func):
        cache = {}
        use_count = Counter()
        kwarg_mark = object()

        @functools.wraps(func)
        def deco(*args, **kwargs):
            key = args
            if kwargs:
                key += (kwarg_mark,) + tuple(sorted(kwargs.items()))

            try:
                result = cache[key]
                use_count[key] += 1
                deco.hits += 1
            except KeyError:
                if len(cache) == max_limit:
                    for k, _ in heapq.nsmallest(max_limit // 10 or 1,
                                                use_count.items(),
                                                key=itemgetter(1)):
                        del cache[k], use_count[k]
                cache[key] = func(*args, **kwargs)
                result = cache[key]
                use_count[key] += 1
                deco.misses += 1
            return result

        deco.hits = deco.misses = 0
        deco.cache = cache
        return deco

    return internal(_func)


@memory
@timer
@cache_deco
def fetch_url(_url):
    return requests.get(_url)


urls = ['https://google.com', 'https://google.com', 'https://youtube.com', 'https://youtube.com', 'https://google.com',
        'https://www.gov.uk', 'https://google.com', 'https://ithillel.ua', 'https://google.com', 'https://youtube.com']
first_n = 100
for url in urls:
    res = fetch_url(url)
    print(res.content[:first_n] if first_n
          else res.content)
