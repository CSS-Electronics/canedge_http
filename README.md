# CANedge HTTP

This repository demonstrates how the [CANedge2](https://www.csselectronics.com/screen/product/can-lin-logger-wifi-canedge2/language/en) can be accessed via HTTP using Python.

The CANedge HTTP interface can e.g. be used to automatically poll and then delete log files from the CANedge2. 

## Project structure
- `canedge_http.py`: CANedge HTTP class
- `canedge_http_example.py` demonstrates how the CANedge HTTP class can be used.

## Installation

Tested with Python 3.8.

## Example of usage 

```python
from pathlib import Path
from canedge_http import CANedgeHTTP

# Configure http connection to CANedge
ce = CANedgeHTTP(host="192.168.0.128")

# Connect
with ce.connect():

    # Loop files in root directory
    for elm, is_dir in ce.list(path=Path("/"), recursive=True):
        print(elm.as_posix())
```

See `canedge_http_example.py` for at more comprehensive example.
