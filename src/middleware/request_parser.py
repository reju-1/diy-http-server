import json
import socket
from typing import Tuple, Dict, Any, Optional
from urllib.parse import unquote_plus


CHUNK_SIZE: int = 1024 * 4  # 4KB


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
    headers["method"], raw_url, headers["version"] = request_line.split(" ")

    headers["url"], headers["query"] = _parse_query_params(raw_url)

    # Parse headers into a dictionary
    for line in headers_list:
        if ": " in line:
            key, value = line.split(": ", 1)

            headers[key.strip()] = _parse_string(value.strip())

    # for header in headers.items():
    #     print(header)

    return headers


def _parse_query_params(raw_url: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Parse query params from the given string.

    Example:
        Input: /url?name=John&age=20
        Return: ('/url', {'name': 'John', 'age': 20})
    """

    if "?" not in raw_url:
        return raw_url, None

    url, param_str = raw_url.split("?", 1)
    query_params = {}

    for param in param_str.split("&"):
        key, value = param.split("=")
        query_params[key] = _parse_string(value)

    return url, query_params


def _parse_string(input_str: str) -> int | float | str:
    """Try to parse a String to number if not possible retune the given string"""

    try:
        return float(input_str) if "." in input_str else int(input_str)
    except ValueError:
        return input_str  # Keep as string if not a number


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


def _parse_url_encoded_body(body: str) -> Dict[str, any]:
    """
    Parses a URL-encoded body string into a dictionary.
    """
    parsed_data = {}

    """key1=value1&key2=value2"""
    pairs = body.split("&")
    for pair in pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)

            key = unquote_plus(key).strip()
            value = unquote_plus(value)

            parsed_data[key] = _parse_string(value)
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
