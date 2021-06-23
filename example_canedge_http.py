import io
import json
from pathlib import Path
from canedge_http import CANedgeHTTP

if __name__ == "__main__":

    # Connect
    with CANedgeHTTP(host="192.168.1.128").connect() as cnt:

        # Loop device
        for elm, is_dir in cnt.list(path=Path("/"), recursive=True):

            print(elm.as_posix())

            # Is dir?
            if is_dir is True:
                continue

            # Is json file?
            if elm.suffix.upper() == ".JSON":

                # Download json file to RAM
                f = io.BytesIO()
                download_res = cnt.download(elm, f)

                if download_res is True:
                    print(json.loads(f.getvalue()))

            # Is log file?
            elif elm.suffix.upper() in [".MF4", ".MFC", ".MFE", ".MFM"]:

                # Download disk location (map device path to relative local path)
                file_local = Path(str(elm)[1:])
                file_local.parent.mkdir(parents=True, exist_ok=True)

                # Download log file to disk
                with open(file_local, 'wb') as f:
                    download_res = cnt.download(elm, f)

                    # Delete file
                    if download_res is True:
                        cnt.delete(elm)
