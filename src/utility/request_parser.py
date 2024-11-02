import json
import socket
from pathlib import Path
from typing import Tuple, Dict
from urllib.parse import unquote_plus


CHUNK_SIZE: int = 1024 * 4  # 4KB


def _parse_url_encoded_body(body: str) -> Dict[str, any]:
    """
    Parses a URL-encoded body string into a dictionary.
    """
    parsed_data = {}

    pairs = body.split("&")
    for pair in pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)

            # Decode and strip each key and value
            parsed_data[unquote_plus(key)] = unquote_plus(value)
        else:
            # For key with no value (e.g., "key=")
            parsed_data[unquote_plus(pair)] = ""

    return parsed_data


def _parse_json_body(body: str) -> Dict[str, any]:
    """
    Parses JSON body data into a dictionary.
    """
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {}  # for invalid Json


def _parse_body(body: str, content_type: str) -> dict | str:
    """
    Parse request body

    Parameters:
        body: str
        content_type: str

    Returns:
        [str or dict]
    """

    content_parser = {
        "application/x-www-form-urlencoded": _parse_url_encoded_body,
        "application/json": _parse_json_body,
    }

    if content_type in content_parser:
        body = content_parser[content_type](body)

    return body


def _parse_header(raw_headers: str) -> Dict[str, any]:
    """
    Parses raw header into a dictionary.

    Parameters:
        raw_headers: str

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

            try:
                headers[key] = float(value) if "." in value else int(value)
            except ValueError:
                headers[key] = value  # Keep as string if not a number

    return headers


def _read_remaining_body(
    client_socket: socket.socket, initial_body: str, content_length: int
) -> str:
    """
    Parameters:
        client_socket: socket
        initial_body: str
        content_length: int

    Returns:
        full_body: str
    """

    remaining_size = content_length - len(initial_body)

    full_body = initial_body

    while remaining_size > 0:
        chunk = client_socket.recv(min(CHUNK_SIZE, remaining_size)).decode()
        full_body += chunk
        remaining_size -= len(chunk)

    return full_body


def request_parser(client_socket: socket.socket) -> Tuple[Dict[str, any], any]:
    """
    Parameters:
        client_socket

    Returns:
        headers: dict
        request_body: any

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
    headers: Dict[str, str | any] = {}

    # Read the request line and headers
    while True:
        chunk = client_socket.recv(CHUNK_SIZE).decode()
        request += chunk
        if "\r\n\r\n" in request:  # Check for header-body separator
            raw_headers, body = request.split("\r\n\r\n", 1)
            break

    headers = _parse_header(raw_headers)

    content_length = 0
    if "Content-Length" in headers:
        content_length = headers["Content-Length"]

    # If body has data, read remaining bytes to complete it
    if content_length > len(body):
        body = _read_remaining_body(client_socket, body, content_length)

    # Parsing body based on Content-Type
    if "Content-Type" in headers:
        # print(f"Before Parsing body: {body}")
        body = _parse_body(body, headers["Content-Type"])

    return headers, body
