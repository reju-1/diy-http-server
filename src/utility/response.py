import socket
from pathlib import Path
from typing import Tuple, Dict

import mimetypes

# Register unsupported MIME types
mimetypes.add_type("video/x-matroska", ".mkv")


CHUNK_SIZE: int = 1024 * 4  # 4KB


def send_file_response(client_socket: socket.socket, headers: str, file_path: str):
    """
    Sends a file response to the client along with Headers
    """

    try:
        # Sending Headers
        client_socket.sendall(headers.encode())

        # Streaming files
        with open(file_path, "rb") as f:
            while data := f.read(CHUNK_SIZE):
                client_socket.sendall(data)

    finally:
        client_socket.close()


def generate_headers(file_name: str) -> str:

    mime_type, _ = mimetypes.guess_type(file_name)
    mime_type = mime_type or "application/octet-stream"  # For Unknown Default is binary

    status = "404 Not Found" if "/not-found.html" in file_name else "200 OK"

    headers = "\r\n".join(
        [
            f"HTTP/1.1 {status}",
            f"Content-Type: {mime_type}",
            "Connection: close",
            "\r\n",
        ]
    )

    return headers


def find_file(file_name: str) -> str:
    """
    Finds the specified file in /public or /views directories.
    Returns 'index.html' if '/' is requested, or 'not-found.html' if the file is missing.
    """

    current_dir = str(Path(__file__).parent)  # path-to-src/utility

    if file_name == "/":
        return f"{current_dir}/../views/index.html"

    # Searching on /views directory
    file_path = Path(f"{current_dir}/../views{file_name}")
    if file_path.exists():
        return str(file_path)

    # Searching on /public directory
    file_path = Path(f"{current_dir}/../../public{file_name}")
    if file_path.exists():
        return str(file_path)

    return f"{current_dir}/../views/not-found.html"
