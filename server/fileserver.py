
import socket
import threading
import os
from datetime import datetime

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
CHUNKSIZE = 4096
SEPARATOR = "<SEPARATOR>"
LOGFILE = "server_log.txt"

def log_event(message):
    with open(LOGFILE, "a") as log:
        log.write(f"[{datetime.now()}] {message}\n")

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")
    try:
        cmd = conn.recv(1024).decode().strip()
        if cmd == "SEND":
            conn.send("OK".encode())
            filenames = conn.recv(1024).decode().strip().split(SEPARATOR)
            for _ in filenames:
                header = conn.recv(1024).decode()
                filename, filesize = header.split(SEPARATOR)
                filesize = int(filesize)
                with open(os.path.basename(filename), "wb") as f:
                    bytes_read = 0
                    while bytes_read < filesize:
                        chunk = conn.recv(min(CHUNKSIZE, filesize - bytes_read))
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_read += len(chunk)
                log_event(f"Received file: {filename} from {addr}")

        elif cmd == "RECEIVE":
            conn.send("OK".encode())
            filenames = conn.recv(1024).decode().strip().split(SEPARATOR)
            for filename in filenames:
                if os.path.exists(filename):
                    filesize = os.path.getsize(filename)
                    conn.send(f"{filename}{SEPARATOR}{filesize}".encode())
                    with open(filename, "rb") as f:
                        while (chunk := f.read(CHUNKSIZE)):
                            conn.sendall(chunk)
                    log_event(f"Sent file: {filename} to {addr}")
                else:
                    conn.send(f"ERROR: File {filename} not found.".encode())
    finally:
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server listening on {SERVER}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
