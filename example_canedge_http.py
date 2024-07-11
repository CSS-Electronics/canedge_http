import io
import json
from pathlib import Path
from canedge_http import CANedgeHTTP

if __name__ == "__main__":

    # Connect
    with CANedgeHTTP(host="192.168.1.143").connect() as cnt:

        # Loop elements on device
        for elm, is_dir in cnt.list(path=Path("/"), recursive=True):

            #print(elm.as_posix())

            # Is dir?
            if is_dir is True:
                continue

            # Is json file?
            elif elm.suffix.upper() == ".JSON":

                # Download json file to RAM
                f = io.BytesIO()
                download_res = cnt.download(elm, f)

                #if download_res is True:
                #    print(json.loads(f.getvalue()))

            # Is log file?
            elif elm.suffix.upper() in [".MF4", ".MFC", ".MFE", ".MFM"]:

                # Download to disk location (map device path to current-working-dir)
                file_local = elm.relative_to("/")
                file_local.parent.mkdir(parents=True, exist_ok=True)

                # Download log file to disk
                with open(file_local, 'wb') as f:
                    download_res = cnt.download(elm, f)

                    # Delete log file on device
                    if download_res is True:
                        cnt.delete(elm)
    pass