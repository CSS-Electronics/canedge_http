import requests

from datetime import datetime, timezone
from requests.auth import HTTPDigestAuth
from requests.adapters import HTTPAdapter
from time import sleep
from typing import BinaryIO
from urllib.parse import urljoin


class CANedgeHTTP:

    def __init__(self, url: str, password: str = None):
        """Create a new instance of CANedgeHTTP"""

        self._api = urljoin(url, "api/")
        self._device_id = None
        self._permission = None
        self._auth = requests.auth.HTTPDigestAuth(username="user", password=password) if password is not None else None

        self._session = requests.Session()

        adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1, pool_block=True)
        self._session.mount("http://", adapter)
        time_to_sleep = None

        with self._session.head(self._api, timeout=5, auth=self._auth) as r:
            if r.status_code == 200 and "Device-id" in r.headers:
                self._device_id = r.headers["Device-id"]
            else:
                raise ValueError(r.reason)
            time_to_sleep = r.elapsed.total_seconds()

        if time_to_sleep is not None:
            sleep(time_to_sleep)
            time_to_sleep = None

        with self._session.options(self._api, timeout=5, auth=self._auth) as r:
            if r.status_code == 200 and "Allow" in r.headers:
                self._permission = r.headers["Allow"]
            else:
                raise ValueError(r.reason)
            time_to_sleep = r.elapsed.total_seconds()

        if time_to_sleep is not None:
            sleep(time_to_sleep)

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def permission(self) -> str:
        return self._permission

    def list(self, path: str = "/", recursive: bool = False) -> dict:
        """List files on device as iterator"""
        path = path[1:] if path.startswith("/") else path
        list_res = {}
        time_to_sleep = None

        with self._session.get(urljoin(self._api, path), auth=self._auth) as r:
            if r.status_code == 200:
                list_res = r.json()
            time_to_sleep = r.elapsed.total_seconds()

        if time_to_sleep is not None:
            sleep(time_to_sleep)

        # Loop elements in path
        for elm in list_res.get("files", []):
            path = urljoin(list_res["path"], elm["name"])

            yield {
                "path": path,
                "is_dir": True if elm["isDirectory"] == 1 else False,
                "lastWritten": datetime.utcfromtimestamp(elm["lastWritten"]).replace(tzinfo=timezone.utc),
                "size": elm["size"]
            }

            if elm["isDirectory"] == 1 and recursive is True:
                yield from self.list(path=path, recursive=recursive)

    def download(self, path: str, f: BinaryIO) -> bool:
        """Download path"""
        path = path[1:] if path.startswith("/") else path
        time_to_sleep = None

        with self._session.get(urljoin(self._api, path), auth=self._auth) as r:
            if r.status_code == 200:
                f.write(r.content)
            time_to_sleep = r.elapsed.total_seconds()

        if time_to_sleep is not None:
            sleep(time_to_sleep)
            return True

        return False

    def delete(self, path: str) -> bool:
        """Delete path"""
        path = path[1:] if path.startswith("/") else path
        time_to_sleep = None
        status_flag = False

        with self._session.delete(urljoin(self._api, path), auth=self._auth) as r:
            if r.status_code == 200:
                status_flag = True
            time_to_sleep = r.elapsed.total_seconds()

        if time_to_sleep is not None:
            sleep(time_to_sleep)

        return status_flag

    pass
