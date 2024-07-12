import argparse
import requests
from datetime import datetime, timezone
from pathlib import Path
from canedge_http import CANedgeHTTP

def download_log_files(endpoint: str, password: str, start_datetime: datetime, end_datetime: datetime) -> None:
    """
    Download log files in time range from CANedge endpoint
    """
    if password is None:
        print(f"Connecting to {endpoint} ... ", end="")
    else:
        print(f"Connecting to {endpoint} with authentication ... ", end="")

    # Create CANedgeHTTP instance
    try:
        http = CANedgeHTTP(endpoint, password)
    except requests.exceptions.ConnectTimeout:
        print("Timeout")
        return
    except Exception as e:
        print(e)
        return
    print("OK")

    # List files on device recursively
    for elm in http.list(path="/", recursive=True):

        elm_path = Path(elm["path"])

        # Is log file?
        if elm_path.suffix.upper() not in [".MF4", ".MFC", ".MFE", ".MFM"]:
            continue

        # Is log file within time range?
        if not (end_datetime >= elm["lastWritten"] >= start_datetime):
            continue

        # Create path in current-working-directory
        file_local = elm_path.relative_to("/")
        file_local.parent.mkdir(parents=True, exist_ok=True)

        # Download to file to path
        print(f"Downloading {elm_path} ({elm['size'] >> 20} MB) -> {file_local.resolve()} ... ", end="")
        with open(file_local, "wb") as f:
            download_res = http.download(elm["path"], f)
        print("OK" if download_res is True else "Fail")

if __name__ == "__main__":

    def valid_datetime_type(arg_datetime_str):
        try:
            return datetime.strptime(arg_datetime_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except ValueError:
            raise argparse.ArgumentTypeError("Invalid datetime")

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("endpoint", type=str, help="CANedge HTTP endpoint, e.g. 192.168.1.100 or 192.168.1.100:80")
    parser.add_argument("--start-datetime", type=valid_datetime_type, default="1900-01-01 00:00", help="Log file start time, e.g. \"2020-01-01 12:00\"")
    parser.add_argument("--end-datetime", type=valid_datetime_type, default="2900-01-01 00:00", help="Log file end time, e.g. \"2020-01-30 20:00\"")
    parser.add_argument("--password", type=str, default=None, help="HTTP authentication password")
    args = parser.parse_args()

    download_log_files(args.endpoint, args.password, args.start_datetime, args.end_datetime)
