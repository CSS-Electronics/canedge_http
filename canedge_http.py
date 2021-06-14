import http.client
import json

from contextlib import contextmanager
from io import IOBase
from pathlib import Path
from typing import Tuple
from urllib.parse import urljoin


class CANedgeHTTP:
    def __init__(self, host: str, port: int = 80):
        """Create a new instance of CANedgeHTTP.
        
        :param host: Remote endpoint (hostname or ip)
        :param port: Remote port
        """
        self._host = host
        self._port = port
        
        self._conn = None

    @contextmanager
    def connect(self):
        try:
            self._conn = http.client.HTTPConnection(self._host, self._port)
            yield self
        finally:
            self._conn.close()
        pass

    def list(self, path: Path, recursive: bool = False) -> Tuple[Path, bool]:
        """List files on device as iterator
        
        :param path: Path
        :param recursive: True to list recursively
        :return: Returns path and if path is directory as a tuple
        """

        self._conn.request("LIST", path.as_posix())
        list_response = self._conn.getresponse()
        if list_response.status == 200:

            # Get response body
            list_res = json.loads(list_response.read().decode())

            # Loop elements in path
            for elm in list_res["files"]:
                path = Path(urljoin(list_res['path'], elm['name']))
                if elm["isDirectory"] == 1:
                    yield path, True
                    if recursive is True:
                        # Recursively list files in dir
                        yield from self.list(path=path, recursive=recursive)
                else:
                    # Return file path
                    yield path, False

    def download(self, path: Path, f: IOBase) -> bool:
        """Download file from path
        
        :param path: Path to resource
        :param f: a file-like object
        :return: True if resource downloaded successfully
        """
        res = False
        self._conn.request("GET", path.as_posix())
        get_response = self._conn.getresponse()
        if get_response.status == 200:
            f.write(get_response.read())
            res = True
        return res

    def delete(self, path: Path) -> bool:
        """Delete a remote path
        
        :param path: Path to resource
        :return: True if resource deleted successfully
        """
        res = False

        self._conn.request("DELETE", path.as_posix())
        if self._conn.getresponse().status == 200:
            res = True
        return res
    
    pass
