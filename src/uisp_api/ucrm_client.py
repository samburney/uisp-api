import pandas as pd

from .uisp_common import UispCommon, GenericObject


class UcrmClient(UispCommon):
    def __init__(self, url: str, app_key: str, port: int = 443, verify_ssl: bool = True):
        super().__init__(url, app_key, port, verify_ssl)

        # Make base_url
        api_path = '/crm/api/v1.0/'
        self.base_url = self._make_base_url(api_path)

        # Get a persistent requests session
        self.conn = self._make_requests_session()

    # Clients
    def new_client(self):
        '''
        Get an instance of the Client object
        '''
        client = Client(self)

        return client

    def get_client(self, client_id):
        '''
        Get an instance of the Client object
        '''
        client = Client(self, client_id)

        return client

    @staticmethod
    def _get_client_type(client_type_id: int):
        '''
        Return named client type

        client_type_id int: clientType as provided from client API
        '''
        client_type = None

        if client_type_id == 1:
            client_type = 'individual'
        elif client_type_id == 2:
            client_type = 'business'
        else:
            raise ValueError('`client_type` must be 1 or 2')

        return client_type

    @staticmethod
    def _get_client_display_name(client):
        '''
        Return client display name

        client dict: Client data as provided from client API
        '''
        client_display_name = None

        # Differentate display names for residential and company clients
        if client['clientType'] == 1:
            client_display_name = f'{client['firstName']} {client['lastName']}'
        elif client['clientType'] == 2:
            client_display_name = f'{client['companyName']}'
        else:
            raise ValueError('`clientType` must be 1 or 2')

        return client_display_name

    # Services
    def new_service(self):
        '''
        Get an instance of the Service object
        '''
        service = Service(self)

        return service

    def get_service(self, service_id):
        '''
        Get an instance of the Service object
        '''
        service = Service(self, service_id)

        return service


class Client(GenericObject):
    '''
    Object representing the `clients/{id}` API method
    '''
    def __init__(self, parent, client_id=None):
        self._id = client_id
        self._schema = 'clients'
        self._endpoint = f'clients/{self._id}'

        # Initialising GenericObject class
        super().__init__(parent)

        # Perform any necessary data sanity updates
        if self._data is not None:
            # Rempve `addressData` attribute as it's redundant
            if 'addressData' in self._data:
                del self._data['addressData']

    @property
    def display_name(self):
        return self._parent._get_client_display_name(self._data)

    @property
    def type(self):
        return self._parent._get_client_type(self.get('clientType'))

    @property
    def services(self):
        services = []
        services_data = self._parent.get_json(f'clients/services?clientId={self._id}', self.use_cache, self.cache_timeout)

        for service_data in services_data:
            service = Service(parent=self._parent, service_id=service_data['id'], _service_data=service_data)
            services.append(service)

        return services

    @property
    def services_df(self):
        services_df = None

        for service in self.services:
            if services_df is None:
                services_df = service.to_df().dropna(axis=1, how='all')
            else:
                services_df = pd.concat([services_df, service.to_df().dropna(axis=1, how='all')], ignore_index=True)

        return services_df


class Service(GenericObject):
    '''
    Object representing the `clients/services/{id}` API method
    '''
    def __init__(self, parent, service_id=None, _service_data=None):
        self._id = service_id
        self._schema = 'services'
        self._endpoint = f'clients/services/{self._id}'

        if _service_data is not None:
            self._data = _service_data

        # Initialising GenericObject class
        super().__init__(parent)

        # Perform any necessary data sanity updates
        # TODO

    @staticmethod
    def _status_map():
        return {
            0: 'prepared',
            1: 'active',
            2: 'ended',
            3: 'suspended',
            4: 'prepared blocked',
            5: 'obsolete',
            6: 'deferred',
            7: 'quoted',
            8: 'inactive',
        }

    @property
    def status(self):
        return Service._status_map()[self.get('status')]

    @property
    def circuit_id(self):
        return self.get_attribute('externalServiceId')['value']

    @property
    def client(self):
        return self._parent.get_client(self.get('clientId'))

    def to_df(self):
        '''
        Return DataFrame of instance data including custom attributes
        '''
        df = pd.json_normalize(self._data)

        # Add custom attributes
        df = df.assign(status_name=self.status)

        return df

    def get_attribute(self, key):
        attributes = self.get('attributes')

        attribute = [attribute for attribute in attributes if attribute['key'] == key][0]

        return attribute
