import time


def benchmark(func):
    """decorator function which is used to calculate execution time of function func.

    Args:
      func: decorated function

    Returns:
      function _benchmark

    """

    def _benchmark(*args, **kwargs):
        t0 = time.time()
        res = func(*args, **kwargs)
        print(f"{func.__name__} elapsed {(time.time() - t0):e} secs")
        return res

    return _benchmark
