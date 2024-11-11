"""This module is for log request"""

import json
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


def log_console(headers: dict, body: str) -> None:
    """Log request to console in tabular format."""

    body_info = body

    # Ensuring body is a string or Dict
    if isinstance(body_info, dict):
        body_info = json.dumps(body)
    elif not isinstance(body, str):
        body_info = ""

    # Defining column widths
    key_width = 20
    value_width = 40
    separator = "+----------------------+------------------------------------------+"

    print("\n\nLog request: ")
    print(separator)
    print(f"| {'Fields':<{key_width}} | {'Values':<{value_width}} |")
    print(separator)

    connection_info = f"{headers['ip']}:{headers['port']}"

    print(f"| {'Connection from':<{key_width}} | {connection_info:<{value_width}} |")
    print(f"| {'Method':<{key_width}} | {headers.get('method'):<{value_width}} |")
    print(f"| {'Request URL':<{key_width}} | {headers['url']:<{value_width}} |")

    if headers.get("query"):
        print(f"| {'Query':<{key_width}} | {headers['query']:<{value_width}} |")

    if body_info:
        print(f"| {'Req-Body':<{key_width}} | {body_info:<{value_width}} |")

    print(separator)
