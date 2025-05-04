import urllib
import urllib3
import requests
import json

import pandas as pd

from pathlib import Path

from .util import Util as util
from .caching import Cache


# Make cache available for use as a decorator
cache = Cache()


class UispCommon:
    def __init__(self, url: str, app_key: str, port: int = 443, verify_ssl: bool = True):
        self._url = url
        self._app_key = app_key
        self._port = port
        self._verify_ssl = verify_ssl
        self._path = Path(__file__).resolve().parent

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
            'Content-Type': 'application/json',
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

            if drop_hashable is True:
                hashable_columns = util.find_hashable_columns(df)

                if len(hashable_columns) > 0:
                    df = df.drop(hashable_columns, axis=1)

        return df


class GenericObject:
    '''
    GenericObject() contains methods and properties common to most data objects
    and is intended to be inherited by them.
    '''
    def __init__(self, parent):
        self._parent = parent
        self._changed = False

        if not hasattr(self, '_id'):
            self._id = None

        # Check endpoint is defined
        if not hasattr(self, '_endpoint') or self._endpoint is None:
            raise ValueError('`endpoint` must be defined')

        # Get schema
        self._jsonschema = None
        if hasattr(self, '_schema'):
            schema_path = Path(parent._path, f'schemas/{self._schema}.json')
            with schema_path.open('r') as file:
                self._jsonschema = json.load(file)

        # Get existing API endpoint data
        self._data = None
        if self._id is not None:
            self._data = parent.get_json(self._endpoint)

        elif self._jsonschema is not None:
            self._data = util.generate_skeleton(self._jsonschema)

        else:
            self._data = None

        # Default list of keys that cannot be modified
        self._immutable_keys = [
            'id',
        ]

    @property
    def id(self):
        return self._id

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def data(self):
        return self._data

    def __call__(self):
        return self._data

    def __str__(self):
        return str(self._data)

    def _check_new_value(self, key, new_value):
        # Ensure immutable values have not been modified
        if key in self._immutable_keys:
            raise ValueError(f'{key} is immutable.')

        # Check new data type matches expected data type
        existing_type = type(self._data[key])
        new_type = type(new_value)
        if existing_type != new_type:
            raise ValueError(f'{key} must be of type {str(existing_type)}.')

        return True

    def get(self, key):
        return self._data[key]

    def set(self, key, new_value):
        '''
        Set individual property to new value
        '''
        self._check_new_value(key, new_value)
        self._data[key] = new_value

        return True

    def update(self, new_data):
        '''
        Update data dictionary
        '''
        # Ensure new values are valid
        for key in new_data.keys():
            self._check_new_value(key, new_data['key'])

        self._data = new_data

        return True

    def save(self):
        '''
        Send updated data to UISP database
        '''
        raise NotImplementedError('The `save()` method has not been implemented.')
