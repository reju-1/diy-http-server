"""This module is for log request"""

import time
from threading import Lock

# For thread-safe file access
file_lock = Lock()


def log_request(dest: str, headers: dict, body: any) -> None:
    """Logs headers, JSON & URL-encoded body to a specified text file"""

    timestamp = time.strftime("%S:%M:%H %d-%m-%Y", time.localtime())

    # Only JSON and Url-encoded are allowed
    permit = ["application/json", "application/x-www-form-urlencoded"]

    permit_body = None
    if "Content-Type" in headers and headers["Content-Type"] in permit:
        permit_body = body

    entry = (
        f"Timestamp: {timestamp}\n"
        f"IP: {headers.get('ip', 'N/A')}\n"
        f"Method: {headers.get('method', 'N/A')}\n"
        f"URL: {headers.get('url', 'N/A')}\n"
        f"Body: {permit_body}\n"
        "===============================================================================\n"
    )

    try:
        with file_lock:
            with open(dest, "a") as f:
                f.write(entry)

    except IOError as e:
        print(f"Failed to write log to {dest}: {e}")
