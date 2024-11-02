import socket
from pathlib import Path
from typing import Tuple, Dict

CHUNK_SIZE: int = 1024 * 4  # 4KB


def _parse_header(raw_headers: str) -> Dict[str, str | int]:
    """
    Parameters:
        raw_header: str

    Returns:
        Header: Dict

    Example:
        "method url version\r\nHeader1: value1\r\nHeader2: value2"
    """

    headers = {}

    request_line, *headers_list = raw_headers.split("\r\n")

    # GET /home HTTP/1.1
    headers["method"], headers["url"], headers["version"] = request_line.split(" ")

    # Parse headers into a dictionary
    for line in headers_list:
        if ": " in line:
            key, value = line.split(": ", 1)

            key = key.strip()
            value = value.strip()

            # Convert value to integer if it represents a number
            if value.isdigit():
                headers[key] = int(value)
            else:
                headers[key] = value

    return headers


# Todo: complete Json or url-encoded parsing
def _parse_body(client_socket: socket.socket, initial_body: str, content_length: int):
    """
    Parameters:
        client_socket: socket
        initial_body: str
        content_length: int

    Returns:
        full_body
    """

    remaining_size = content_length - len(initial_body)

    full_body = initial_body

    while remaining_size > 0:
        chunk = client_socket.recv(min(CHUNK_SIZE, remaining_size)).decode()
        full_body += chunk
        remaining_size -= len(chunk)

    return full_body


def request_parser(client_socket: socket.socket) -> Tuple[Dict[str, str | int], str]:
    """
    Parameters:
        client_socket

    Returns:
        headers: dict
        request_body: str

    Notes:
        Simplified HTTP1.1 req/res structure:
            request = request-line + Headers + "\r\n\r\n" + Body (optional)
            response = status-line + Headers + "\r\n\r\n" + Body (optional)

        --------------------------------------------------------------------------------------------------------------------
        Sample HTTP1.1 Request:
        POST /submit HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 27\r\n\r\nname=rejo&age=21
        Sample HTTP1.1 Response:
        HTTP/1.1 200 OK\r\nContent-Type: Application/json\r\nContent-Length: 37\r\n\r\n{status: "User updated successfully"}
        --------------------------------------------------------------------------------------------------------------------
    """

    request = ""
    raw_headers = ""

    body = ""
    headers: Dict[str, str | int] = {}

    # Read the request line and headers
    while True:
        chunk = client_socket.recv(CHUNK_SIZE).decode()
        request += chunk
        if "\r\n\r\n" in request:
            raw_headers, body = request.split("\r\n\r\n", 1)  # Split headers and body
            break

    headers = _parse_header(raw_headers)

    content_length = 0
    if "Content-Length" in headers:
        content_length = headers["Content-Length"]

    # If body has data, read remaining bytes to complete it
    if content_length > len(body):
        body = _parse_body(client_socket, body, content_length)

    return (headers, body)
