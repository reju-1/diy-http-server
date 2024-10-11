import socket
from pathlib import Path
from typing import Tuple

CHUNK_SIZE: int = 1024 * 4  # 4KB


def _request_parser(client_socket: socket.socket) -> Tuple[str, str]:
    """
    Parameters:
        client_socket

    returns:
        request_headers
        request_body

    Notes:
        Simplified HTTP req/res structure:
            HTTP req/res = First_line + Headers + "\r\n\r\n" + xyz-Bytes-Body

        Note: First_line contains Request-info ro Status-info.
        Request-info eg: GET /home HTTP/1.1    (for http Request)
        Status-info  eg: HTTP/1.1 200 OK       (for http Request)

        HTTP headers convey metadata between client and server,
        specifying req/res details like content type, length, accept, caching, and authentication.

        example: Content-Length:50  ## 50 byte of body in the request/response .


    Sample HTTP1.1 Request:
    -----------------------------------------------------------------------------------------------------------------------------------------
    POST /submit HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 27\r\n\r\nname=rejo&age=21
    -----------------------------------------------------------------------------------------------------------------------------------------
    Sample HTTP1.1 Response:
    --------------------------------------------------------------------------------------------------------------------
    HTTP/1.1 200 OK\r\nContent-Type: Application/json\r\nContent-Length: 37\r\n\r\n{status: "User updated successfully"}
    --------------------------------------------------------------------------------------------------------------------
    """

    request = ""
    while True:
        # print('\nReading....')
        chunk = client_socket.recv(CHUNK_SIZE).decode()  # Blocking code
        print(f"Chunk len: {len(chunk)}\nContent: {repr(chunk)}\n")

        if not chunk:
            break

        request += chunk

        # Check if the full HTTP headers are received
        if "\r\n\r\n" in request:
            break

    headers = request.split("\r\n\r\n")[0]
    body = ""  # write code for reading request-body

    return headers, body


# type alias ip:port
socket_address = Tuple[str, int]


def client_handler(client_socket: socket.socket, address: socket_address) -> None:
    print(f"Accepted connection from {address[0]}:{address[1]}")

    try:
        headers, _ = _request_parser(client_socket)

        first_line = headers.split("\r\n")[0]  # GET /home.html HTTP/1.1
        req_url = first_line.split(" ")[1]

        if req_url == "/favicon.ico":
            # wright code for favicon.ico
            client_socket.close()
            return

        req_file_path = Path(f"./views{req_url}")  # eg: ./views/index.html

        res_file = ""
        res_header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n\r\n"
        )

        if req_url == "/":
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
            binary_html_content = f.read()

        client_socket.sendall(res_header.encode())
        client_socket.sendall(binary_html_content)

    finally:
        client_socket.close()
