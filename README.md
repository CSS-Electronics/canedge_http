# CANedge HTTP
Python module for accessing the [CANedge2](https://www.csselectronics.com/screen/product/can-lin-logger-wifi-canedge2/language/en) via HTTP. The CANedge2 HTTP interface can e.g. be used to automatically poll and then delete log files from the CANedge2. 

The module supports download, deletion, and listing of files on the CANedge2.

## Installation
```
pip install canedge_http
```

## Usage examples
See `example_canedge_http.py` for a more comprehensive example.

### Import
```python
from canedge_http import CANedgeHTTP
```

### Connect
```python
with CANedgeHTTP(host="192.168.0.128").connect() as cnt:
    ...
```

### LIST
```python
for elm, is_dir in cnt.list(path=Path("/"), recursive=True):
   ...
```

### Download
Download takes a file-like object

```python
f = io.BytesIO()
res = cnt.download(elm, f)
```
or
```python
with open("somefile", 'wb') as f:
    res = cnt.download(elm, f)
```

### Delete
```python
res = cnt.delete(elm)
```

## Test
Tests are implemented using pytest and can be found in `test_canedge_http.py`.