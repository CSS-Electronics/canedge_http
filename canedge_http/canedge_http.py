import http.client
import json
from contextlib import contextmanager
from io import IOBase
from pathlib import Path
from time import sleep
from typing import Tuple
from urllib.parse import urljoin


class CANedgeHTTP:

    @staticmethod
    def request_and_response(conn: http.client.HTTPConnection, method: str, path: Path):
        """
        Helper function to reliably perform a request and receive a response from the CANedge (limited to one socket).
        If the CANedge is busy, it closes the socket without data.
        """
        status = None
        payload = None
        for retry in range(1, 5):
            conn.request(method, path.as_posix())
            try:
                list_response = conn.getresponse()
                status = list_response.status
                payload = list_response.read()
            except http.client.RemoteDisconnected:
                pass
            finally:
                # Allow the socket time to completely close
                sleep(retry ** 2 * 0.1)
                if status is not None and payload is not None:
                    break

        return status, payload

    def __init__(self, host: str, port: int = 80):
        """Create a new instance of CANedgeHTTP.
        
        :param host: Remote endpoint (hostname or ip)
        :param port: Remote port
        """
        self._host = host
        self._port = port
        self._conn = None

    @contextmanager
    def connect(self) -> http.client.HTTPConnection:
        try:
            self._conn = http.client.HTTPConnection(self._host, self._port, timeout=10)
            self._conn.set_debuglevel(1)
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
        status, payload = self.request_and_response(self._conn, "LIST", path)
        if status == 200:

            # Parse payload
            list_res = json.loads(payload.decode())

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
        """Download path

        :param path: Path to resource
        :param f: a file-like object
        :return: True if resource downloaded successfully
        """
        res = False

        status, payload = self.request_and_response(self._conn, "GET", path)
        if status == 200:
            f.write(payload)
            res = True
        return res

    def delete(self, path: Path) -> bool:
        """Delete path

        :param path: Path to resource
        :return: True if resource deleted successfully
        """
        res = False

        status, payload = self.request_and_response(self._conn, "DELETE", path)
        if status == 200:
            res = True
        return res
    
    pass
