import socket
from pathlib import Path
from typing import Tuple

from utility.request_parser import request_parser


# type alias ip:port
socket_address = Tuple[str, int]


def client_handler(client_socket: socket.socket, address: socket_address) -> None:
    print(f"Accepted connection from {address[0]}:{address[1]}")

    try:
        headers, body = request_parser(client_socket)

        print(f"\nrequest url: {headers["url"]}")
        # print(f"request headers: {headers}")
        print(f"request body: {body}\n")

        req_url = headers["url"]

        req_file_path = Path(f"./views{req_url}")  # eg: ./views/index.html

        res_file = ""
        res_header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n\r\n"
        )

        if req_url == "/favicon.ico":
            res_file = "./views/favicon.svg"
            res_header = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: image/svg+xml\r\n"
                "Connection: close\r\n\r\n"
            )

        elif req_url == "/":
            res_file = "./views/index.html"

        elif req_file_path.exists() and req_file_path.is_file():
            res_file = str(req_file_path)

        else:
            res_file = "./views/not-found.html"

            res_header = (
                "HTTP/1.1 404 not found\r\n"
                "Content-Type: text/html\r\n"
                "Connection: close\r\n\r\n"
            )

        with open(res_file, "rb") as f:
            # apply stream response
            file_content = f.read()

        client_socket.sendall(res_header.encode())
        client_socket.sendall(file_content)

    finally:
        client_socket.close()
