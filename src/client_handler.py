import socket
from typing import Tuple

from constant import LOG_ADDRESS
from middleware.request_parser import request_parser
from utility.logger import log_request
from utility.response import find_file, send_file_response
from api.routes import send_json_response

# type alias ip:port
socket_address = Tuple[str, int]


def client_handler(client_socket: socket.socket, address: socket_address) -> None:
    print(f"Accepted connection from {address[0]}:{address[1]}")

    headers, body = request_parser(client_socket)

    headers["ip"] = address[0]
    headers["port"] = address[1]

    print(f"\nrequest url: {headers['url']}")
    print(f"request body: {body}\n")

    log_request(LOG_ADDRESS, headers, body)

    if headers.get("Accept") == "application/json" or "/api" in headers.get("url", ""):
        return send_json_response(socket=client_socket, headers=headers)

    res_file = find_file(headers["url"])
    send_file_response(client_socket, res_file)
