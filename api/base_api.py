import logging

import requests

logger = logging.getLogger(__name__)


class BaseApi:
    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def _request(self, method, path, **kwargs):
        url = self.base_url + path
        logger.info(f"{method} {url}")

        if "json" in kwargs:
            logger.info(f"Тело запроса: {kwargs['json']}")

        response = self.session.request(method, url, **kwargs)

        logger.info(f"Код ответа: {response.status_code}")
        logger.info(f"Тело ответа: {response.text}")
        return response

    def get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def patch(self, path, **kwargs):
        return self._request("PATCH", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)