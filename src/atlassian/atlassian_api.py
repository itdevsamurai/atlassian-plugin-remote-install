import logging
from json import dumps as json_dumps

import requests


class AtlassianServerAPIHeaders:
    DEFAULT = {"Content-Type": "application/json", "Accept": "application/json"}
    EXPERIMENTAL = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-ExperimentalApi": "opt-in",
    }
    FORM_TOKEN = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Atlassian-Token": "no-check",
    }
    NO_CHECK = {"X-Atlassian-Token": "no-check"}
    SAFE_MODE = {
        "X-Atlassian-Token": "nocheck",
        "Content-Type": "application/vnd.atl.plugins.safe.mode.flag+json",
    }
    EXPERIMENTAL_GENERAL = {
        "X-Atlassian-Token": "no-check",
        "X-ExperimentalApi": "opt-in",
    }


class AtlassianServerAPI:
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        session: requests.Session | None = None,
        timeout: float = 30,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.url = url.strip("/")
        self.timeout = timeout
        if session is None:
            self._session = requests.Session()
        else:
            self._session = session
        self._session.auth = (username, password)

    def _update_header(self, key, value):
        self._session.headers.update({key, value})

    def request(
        self,
        path: str = "/",
        url: str = "",
        method: str = "GET",
        headers=None,
        data=None,
        json=None,
        files=None,
        allow_redirects: bool = True,
        timeout: float = 0,
    ):
        if headers is None:
            headers = AtlassianServerAPIHeaders.DEFAULT
        if files is None:
            if data:
                data = json_dumps(data)
            if json:
                json = json_dumps(data)

        req_url = f"{self.url}{path}"
        if url:
            req_url = url

        res = self._session.request(
            method=method,
            url=req_url,
            headers=headers,
            data=data,
            json=json,
            files=files,
            timeout=timeout if timeout else self.timeout,
            allow_redirects=allow_redirects,
        )
        res.raise_for_status()
        return res
