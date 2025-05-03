import inspect
import functools
import flask
import flask_caching
import hashlib


class Cache:
    '''
    uisp_api.caching.Cache()

    Provides access to the Flask Caching extension in a way that allows configuration
    to be passed from the uisp_api classes at runtime.
    '''
    def __init__(self):
        pass

    def __call__(self, cache_config):
        '''
        Return a configured instance of `flask_caching.Cache()`
        '''
        return self._get_cache(cache_config)

    def _get_cache(self, cache_config):
        '''
        Return a configured instance of `flask_caching.Cache()`
        '''
        return flask_caching.Cache(app=flask.Flask(__name__), config=cache_config)

    def cached(self, *decorator_args, **decorator_kwargs):
        '''
        A decorator which wraps the `flask_caching.Cache.cached()` decorator such
        that configuration may be provided at runtime via the decorated function's
        `self` argument.
        '''
        def decorator(f):
            @functools.wraps(f)
            def wrapper(cls, *func_args, **func_kwargs):
                cache = self._get_cache(cls.cache_config)
                return cache.cached(*decorator_args, **decorator_kwargs)(f)(cls, *func_args, **func_kwargs)

            return wrapper

        return decorator

    def memoize(self, *decorator_args, **decorator_kwargs):
        '''
        A decorator which wraps the `flask_caching.Cache.memoize()` decorator such
        that configuration may be provided at runtime via the decorated function's
        `self` argument.
        '''
        def decorator(f):
            @functools.wraps(f)
            def wrapper(cls, *func_args, **func_kwargs):
                cache = self._get_cache(cls.cache_config)
                return cache.memoize(*decorator_args, **decorator_kwargs)(f)(cls, *func_args, **func_kwargs)

            return wrapper

        return decorator

    def make_cache_key(self, prefix, **kwargs):
        sorted_kwargs = sorted(kwargs.items())
        hashed_kwargs = hashlib.md5(str(sorted_kwargs).encode()).hexdigest()

        cache_key = f'{prefix}_{hashed_kwargs}'

        return cache_key

    def make_func_cache_key(self, dict):
        f = inspect.currentframe().f_back.f_code
        f_name = f.co_name

        return self.make_cache_key(f_name, **dict)
