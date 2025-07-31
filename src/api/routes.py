import json
import socket
from pathlib import Path
from datetime import datetime
from constant import PUBLIC_DIR

content_path = Path(PUBLIC_DIR)


def send_json_response(socket: socket.socket, headers: dict[str, any]) -> None:
    """Send json response to client"""

    file_info = _get_files(headers["url"])

    file_info_json = json.dumps(file_info)

    response_headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    socket.sendall(response_headers.encode("utf-8"))
    socket.sendall(file_info_json.encode("utf-8"))


def _get_files(path: str = "/") -> json:
    """Get all the file in given path along with name, size, las_modified"""

    files = []
    for f in content_path.iterdir():
        if f.is_file():
            file_info = {
                "file-name": f.name,
                "size": _convert_size(f.stat().st_size),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
            files.append(file_info)

    return files


def _convert_size(size_bytes: int) -> str:
    """Convert number of Bytes to B/KB/MB/GB"""

    if size_bytes == 0:
        return "0 B"

    # Defining units in increments of 1024
    size_units = ["B", "KB", "MB", "GB", "TB"]
    i = 0

    while size_bytes >= 1024 and i < len(size_units) - 1:
        size_bytes /= 1024
        i += 1

    return f"{size_bytes:.1f} {size_units[i]}"
