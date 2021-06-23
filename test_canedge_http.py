import io
import json
import re
import pytest
from http import HTTPStatus
from pathlib import Path
from werkzeug import Response
from canedge_http import CANedgeHTTP
from pytest_httpserver import HTTPServer


class TestCANedgeHTTP(object):

    _fs = None

    file_list = [
        "config-XX.XX.json",
        "schema-XX.XX.json",
        "LOG/AABBCCDD/00000001/00000001.MF4",
        "LOG/AABBCCDD/00000001/00000002.MF4",
        "LOG/AABBCCDD/00000002/00000001.MF4",
        "LOG/AABBCCDD/00000002/00000002.MF4",
    ]

    def get_handler(self, request):

        # Map to local path
        p = Path(self._fs).joinpath(request.path[1:])

        res = Response()
        if p.exists():
            res.status = HTTPStatus.OK
            with open(p, 'r') as f:
                res.response = f.read()
        else:
            res.status = HTTPStatus.NOT_FOUND
        return res

    def delete_handler(self, request):

        # Map to local path
        p = Path(self._fs).joinpath(request.path[1:])

        res = Response()
        if p.exists():
            res.status = HTTPStatus.OK
            p.unlink()
        else:
            res.status = HTTPStatus.NOT_FOUND
        return res

    def list_handler(self, request):

        # Map to local path
        p = Path(self._fs).joinpath(request.path[1:])

        res = Response()
        if p.exists():
            res.status = HTTPStatus.OK
            res.response = json.dumps(
                {
                    "path": request.path + "/",
                    "files": [{"name": x.name,
                               "lastWritten": 0,
                               "size": 0,
                               "isDirectory": 1 if x.is_dir() else 0
                               } for x in p.iterdir()]
                }
            )
        else:
            res.status = HTTPStatus.NOT_FOUND
        return res

    @pytest.fixture()
    def fs(self, tmpdir):

        for file in self.file_list:

            file_path = Path(tmpdir).joinpath(file)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w') as f:
                f.write(file_path.name)

        return tmpdir

    @pytest.fixture()
    def httpserver_config(self, httpserver: HTTPServer, fs):
        """ Configure the http server handlers """

        # Set fs to be used by handlers (handlers take no data input)
        self._fs = fs

        # Handlers for GET, DELETE and LIST requests
        httpserver.expect_request(uri=re.compile("^/"), method="GET").respond_with_handler(self.get_handler)
        httpserver.expect_request(uri=re.compile("^/"), method="DELETE").respond_with_handler(self.delete_handler)
        httpserver.expect_request(uri=re.compile("^/"), method="LIST").respond_with_handler(self.list_handler)
        return httpserver

    @pytest.fixture()
    def ce(self, httpserver_config: HTTPServer):
        return CANedgeHTTP(host="localhost", port=httpserver_config.port)

    @pytest.mark.parametrize("uri", file_list)
    def test_download_exists(self, httpserver_config: HTTPServer, fs, ce, uri):
        """ Download existing files"""
        res = None
        with ce.connect() as cnt:
            f = io.BytesIO()
            res = cnt.download(Path(uri), f)
        assert res is True
        assert f.getvalue().decode() == Path(uri).name

    @pytest.mark.parametrize("uri", ["dummy.txt"])
    def test_download_not_exists(self, httpserver_config: HTTPServer, fs, ce, uri):
        """Attempt to download non-existing files"""
        res = None
        with ce.connect() as cnt:
            f = io.BytesIO()
            res = cnt.download(Path(uri), f)
        assert res is False

    @pytest.mark.parametrize("uri", file_list)
    def test_delete_exists(self, httpserver_config: HTTPServer, fs, ce, uri):
        """Delete existing files"""
        res = None
        with ce.connect() as cnt:
            res = cnt.delete(path=Path(uri))
        assert res is True

    @pytest.mark.parametrize("uri", ["dummy.txt"])
    def test_delete_exists(self, httpserver_config: HTTPServer, fs, ce, uri):
        """Attempt to delete non-existing files"""
        res = None
        with ce.connect() as cnt:
            res = cnt.delete(path=Path(uri))
        assert res is False

    @pytest.mark.parametrize("uri", list(set([Path("/").joinpath(Path(x).parent) for x in file_list])))
    def test_list(self, httpserver_config: HTTPServer, fs, ce, uri):
        """Simple test of LIST"""
        res = None
        with ce.connect() as cnt:
            for elm, is_dir in cnt.list(path=Path(uri), recursive=False):
                # At least one element found, set result
                res = True
        assert res is True
