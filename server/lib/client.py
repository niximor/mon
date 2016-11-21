import requests
from urllib.parse import urljoin


class Client:
    """
    Mon API Client.
    """

    def __init__(self, api_root: str):
        """
        :param api_root: URL where the API can be reached.
        """
        self.api_root = api_root

        # Ensure trailing slash in api root
        if self.api_root[-1] != "/":
            self.api_root += "/"

    def get(self, method: str, params: dict=None) -> any:
        """
        Performs GET request to the API.
        :param method: Method to call
        :param params: Optional params to pass as query string.
        :return: Passes data returned by API.
        """
        return self._process_response("GET", method, requests.get(self._api_url(method), params=params))

    def post(self, method: str, json: any=None) -> any:
        """
        Performs POST request to the API.
        :param method: Method to call
        :param json: Optional data to pass as JSON payload.
        :return: Passes data returned by API.
        """
        return self._process_response("POST", method, requests.post(self._api_url(method), json=json))

    def put(self, method: str, json: any=None) -> any:
        """
        Performs PUT request to the API.
        :param method: Method to call
        :param json: Optional data to pass as JSON payload.
        :return: Passes data returned by API.
        """
        return self._process_response("PUT", method, requests.put(self._api_url(method), json=json))

    def patch(self, method: str, json: any=None) -> any:
        """
        Performs PATCH request to the API.
        :param method: Method to call
        :param json: Optional data to pass as JSON payload.
        :return: Passes data returned by API.
        """
        return self._process_response("PATCH", method, requests.patch(self._api_url(method), json=json))

    def delete(self, method: str, params: dict=None) -> any:
        """
        Performs DELETE request to the API.
        :param method: Method to call
        :param params: Optional params to pass as query string.
        :return: Passes data returned by API.
        """
        return self._process_response("DELETE", method, requests.delete(self._api_url(method), params=params))

    def _api_url(self, method: str) -> str:
        """
        Return URL to the API method.
        :param method: API method relative to api root.
        :return: URL
        """
        # Trim leading slash from method name.
        if method[:1] == "/":
            method = method[1:]

        if method[:-1] != "/":
            method += "/"

        return urljoin(self.api_root, method)

    @staticmethod
    def _process_response(http_method: str, method: str, resp: requests.Response) -> any:
        """
        Process response and return json data, otherwise raise ApiError.
        :param http_method: HTTP method name for correct error reporting.
        :param method: Method name for correct error reporting.
        :param resp: Response from the API
        :return: JSON data or throws ApiError.
        """
        if resp.status_code == 200:
            return resp.json()
        else:
            try:
                response = resp.json()
                raise ApiError(http_method, method, resp.status_code, response)
            except ValueError:
                raise ApiError(http_method, method, resp.status_code, "")


class ApiError(Exception):
    """
    Base exception thrown when call to API fails.
    """
    def __init__(self, http_method, method, http_status, http_status_message=""):
        self.http_method = http_method
        self.method = method
        self.http_status = http_status
        self.http_status_message = http_status_message

        super(ApiError, self).__init__("API Method %s %s failed with status %d: %s" %
                                       (self.http_method, self.method, self.http_status, self.http_status_message))
