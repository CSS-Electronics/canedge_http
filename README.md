# CANedge HTTP
Python module for accessing the [CANedge](https://www.csselectronics.com/pages/can-bus-hardware-products) via HTTP. The CANedge HTTP interface can e.g. be used to automatically poll and then delete log files stored on the CANedge. 

The module supports download, deletion, and listing of files on the CANedge.

## Installation
```
pip install canedge_http
```

## Demos
- `demo_download_log_files.py` download log files filtered by start and end-time

## Usage

### Import
```python
from canedge_http import CANedgeHTTP
```

### Construct

```python
http = CANedgeHTTP("192.168.1.100")
```

### Device ID

```python
http.device_id
```
Result example:
```python
'AABBCCDD'
```

### Permission

```python
http.permission
```
Result example:
```python
'OPTIONS, GET, HEAD, PUT, DELETE'
```

### List files
```python
for elm in http.list(path="/", recursive=True):
   ...
```
Result example (elm):
```python
{'path': '/device.json', 'is_dir': False, 'lastWritten': datetime.datetime(2024, 7, 12, 5, 3, 12, tzinfo=datetime.timezone.utc), 'size': 601}
```

### Download
Download takes a file-like object, e.g.

```python
f = io.BytesIO()
http.download("/device.json", f)
```
or
```python
with open("00000001.MF4", "wb") as f:
    http.download("/LOG/AABBCCDD/00000001/00000001.MF4", f)
```

### Delete
```python
http.delete("/LOG/AABBCCDD/00000001/00000001.MF4")
```
