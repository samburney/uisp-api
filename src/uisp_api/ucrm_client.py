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
    def services(self, use_cache=True, cache_timeout=60):
        return self._parent.get_json(f'clients/services?clientId={self._id}', use_cache, cache_timeout)


class Service(GenericObject):
    '''
    Object representing the `clients/services/{id}` API method
    '''

    def __init__(self, parent, service_id=None):
        self._id = service_id
        self._schema = 'services'
        self._endpoint = f'clients/services/{self._id}'

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
