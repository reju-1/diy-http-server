import socket
from typing import Tuple

from utility.request_parser import request_parser
from utility.response import find_file, generate_headers, send_file_response


# type alias ip:port
socket_address = Tuple[str, int]


def client_handler(client_socket: socket.socket, address: socket_address) -> None:
    print(f"Accepted connection from {address[0]}:{address[1]}")
    
    headers, body = request_parser(client_socket)

    # print(f"request headers: {headers}")
    print(f"\nrequest url: {headers["url"]}")
    print(f"request body: {body}\n")

    # Todo: Save Request body

    res_file = find_file(headers["url"])
    res_headers = generate_headers(res_file)
    send_file_response(client_socket,res_headers, res_file )
