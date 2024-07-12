import requests
from datetime import datetime, timezone
from typing import BinaryIO
from urllib.parse import urljoin
from requests.auth import HTTPDigestAuth


class CANedgeHTTP:

    def __init__(self, url: str, password: str = None):
        """Create a new instance of CANedgeHTTP"""

        self._api = urljoin( url,"api/")
        self._device_id = None
        self._permission = None
        self._auth = requests.auth.HTTPDigestAuth(username="user", password=password) if password is not None else None

        r = requests.head(self._api, timeout=5, auth=self._auth)
        if r.status_code == 200 and "Device-id" in r.headers:
            self._device_id = r.headers["Device-id"]
        else:
            raise ValueError(r.reason)

        r = requests.options(self._api, timeout=5, auth=self._auth)
        if r.status_code == 200 and "Allow" in r.headers:
            self._permission = r.headers["Allow"]
        else:
            raise ValueError(r.reason)

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def permission(self) -> str:
        return self._permission

    def list(self, path: str = "/", recursive: bool = False) -> dict:
        """List files on device as iterator"""
        path = path[1:] if path.startswith("/") else path

        r = requests.get(urljoin(self._api, path), auth=self._auth)
        if r.status_code == 200:

            list_res = r.json()

            # Loop elements in path
            for elm in list_res.get("files", []):

                path = urljoin(list_res["path"], elm["name"])

                yield {"path": path,
                        "is_dir": True if elm["isDirectory"] == 1 else False,
                        "lastWritten": datetime.utcfromtimestamp(elm["lastWritten"]).replace(tzinfo=timezone.utc),
                        "size": elm["size"]}

                if elm["isDirectory"] == 1 and recursive is True:
                        yield from self.list(path=path, recursive=recursive)

    def download(self, path: str, f: BinaryIO) -> bool:
        """Download path"""
        path = path[1:] if path.startswith("/") else path

        r = requests.get(urljoin(self._api, path), auth=self._auth)
        if r.status_code == 200:
            f.write(r.content)
        return True if r.status_code == 200 else False

    def delete(self, path: str) -> bool:
        """Delete path"""
        path = path[1:] if path.startswith("/") else path

        r = requests.delete(urljoin(self._api, path), auth=self._auth)
        return True if r.status_code == 200 else False
