import os
import socket
import threading
from pathlib import Path
from client_handler import client_handler


HOST: str = "localhost"
PORT: int = 8080


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # allows reusing the address/port for restarting the server.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(10)
        print(f"Server running on http://{HOST}:{PORT}\n")

        try:
            while True:
                client_socket, client_address = server_socket.accept()

                # assigning separate thread for each client
                client_thread = threading.Thread(
                    target=client_handler, args=(client_socket, client_address)
                )
                # Allow thread to exit when the main program exits
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("\nShutting down the server.")


if __name__ == "__main__":
    main()
