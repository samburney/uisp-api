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
        client = _Clients(self)

        return client

    def get_client(self, client_id):
        '''
        Get an instance of the Client object
        '''
        client = _Clients(self, client_id)

        return client


class _Clients(GenericObject):
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
