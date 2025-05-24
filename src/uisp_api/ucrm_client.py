from .uisp_common import UispCommon, GenericObject


class UcrmClient(UispCommon):
    def __init__(self, url: str, app_key: str, port: int = 443, verify_ssl: bool = True):
        super().__init__(url, app_key, port, verify_ssl)

        # Make base_url
        api_path = '/crm/api/v1.0/'
        self.base_url = self._make_base_url(api_path)

        # Get a persistent requests session
        self.conn = self._make_requests_session()

    def new_client(self):
        '''
        Get an instance of the Client object
        '''
        client = _Client(self)

        return client

    def get_client(self, client_id):
        '''
        Get an instance of the Client object
        '''
        client = _Client(self, client_id)

        return client

    def new_service(self):
        '''
        Get an instance of the Service object
        '''
        service = _Service(self)

        return service

    def get_service(self, service_id):
        '''
        Get an instance of the Service object
        '''
        service = _Service(self, service_id)

        return service


class _Client(GenericObject):
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


class _Service(GenericObject):
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
        return _Service._status_map()[self.get('status')]
