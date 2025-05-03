from .uisp_common import UispCommon


class UcrmClient(UispCommon):
    def __init__(self, url: str, app_key: str, port: int = 443, verify_ssl: bool = True):
        super().__init__(url, app_key, port, verify_ssl)

        # Make base_url
        api_path = '/crm/api/v1.0/'
        self.base_url = self._make_base_url(api_path)

        # Get a persistent requests session
        self.conn = self._make_requests_session()
