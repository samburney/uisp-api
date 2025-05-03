import urllib
import urllib3
import requests

import pandas as pd

from .caching import Cache


# Make cache available for use as a decorator
cache = Cache()


class UispCommon:
    def __init__(self, url: str, app_key: str, port: int = 443, verify_ssl: bool = True):
        self._url = url
        self._app_key = app_key
        self._port = port
        self._verify_ssl = verify_ssl

        # Disable Insecure HTTPS warning
        if self._verify_ssl is False:
            urllib3.disable_warnings()

        # Placeholder for self.conn
        self.conn = None

        # **TODO** cache config
        self.cache_config = {
            'DEBUG': True,
            'CACHE_TYPE': 'FileSystemCache',
            'CACHE_DIR': 'FileSystemCache',
        }
        self.cache = cache(self.cache_config)

    def _make_base_url(self, api_path: str):
        parsed_url = urllib.parse.urlparse(self._url)

        # Validate provided URL
        if parsed_url.scheme is None:
            raise ValueError("Provided URL must include scheme component; for example 'https://<your url>/'")

        if parsed_url.netloc is None:
            raise ValueError("Provided URL must include host component")

        # Make a cleaned version of provided URL
        cleaned_url = urllib.parse.urlunsplit([parsed_url.scheme, parsed_url.netloc, parsed_url.path, str(self._port), None])

        # Make API URL
        base_url = urllib.parse.urljoin(cleaned_url, api_path)

        return base_url

    def _make_requests_session(self):
        s = requests.Session()

        headers = {
            'X-Auth-App-Key': self._app_key,
        }

        s = requests.Session()
        s.headers = headers
        s.verify = self._verify_ssl

        return s

    def make_url(self, endpoint: str):
        endpoint = endpoint.strip('/')

        return urllib.parse.urljoin(self.base_url, endpoint)

    def get_json(self, endpoint: str, use_cache=True):
        json = None
        url = self.make_url(endpoint)
        cache_key = cache.make_func_cache_key({'endpoint': endpoint})

        if self.cache.has(cache_key) and use_cache is True:
            return self.cache.get(cache_key)
        else:
            resp = self.conn.get(url)
            if resp.status_code == 200:
                json = resp.json()
                self.cache.set(cache_key, json, 60)

        return json

    def get_dataframe(self, endpoint: str, drop_hashable: bool = True, use_cache=True):
        df = None
        json = self.get_json(endpoint=endpoint, use_cache=use_cache)

        if json is not None:
            df = pd.DataFrame(json)

        return df
