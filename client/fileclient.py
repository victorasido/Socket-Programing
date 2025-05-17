
import socket
import os
from tqdm import tqdm
from datetime import datetime

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
CHUNKSIZE = 4096
SEPARATOR = "<SEPARATOR>"
LOGFILE = "client_log.txt"

def log_event(message):
    with open(LOGFILE, "a") as log:
        log.write(f"[{datetime.now()}] {message}\n")

def send_files(filenames):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(ADDR)
        client.send(b"SEND")
        if client.recv(1024).decode().strip() == "OK":
            client.send(SEPARATOR.join(filenames).encode())
            for filename in filenames:
                if os.path.exists(filename):
                    filesize = os.path.getsize(filename)
                    client.send(f"{filename}{SEPARATOR}{filesize}".encode())
                    with open(filename, "rb") as f, tqdm(total=filesize, unit='B', unit_scale=True, desc=filename) as progress:
                        while (chunk := f.read(CHUNKSIZE)):
                            client.sendall(chunk)
                            progress.update(len(chunk))
                    log_event(f"Sent file: {filename}")
                else:
                    print(f"File not found: {filename}")

def receive_files(filenames):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(ADDR)
        client.send(b"RECEIVE")
        if client.recv(1024).decode().strip() == "OK":
            client.send(SEPARATOR.join(filenames).encode())
            for _ in filenames:
                header = client.recv(1024).decode()
                if header.startswith("ERROR"):
                    print(header)
                    continue
                filename, filesize = header.split(SEPARATOR)
                filesize = int(filesize)
                with open(os.path.basename(filename), "wb") as f, tqdm(total=filesize, unit='B', unit_scale=True, desc=filename) as progress:
                    bytes_read = 0
                    while bytes_read < filesize:
                        chunk = client.recv(min(CHUNKSIZE, filesize - bytes_read))
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_read += len(chunk)
                        progress.update(len(chunk))
                log_event(f"Received file: {filename}")

def menu():
    while True:
        print("\n1. Kirim file ke server")
        print("2. Ambil file dari server")
        print("3. Keluar")
        choice = input("Pilih opsi (1/2/3): ").strip()

        if choice == "1":
            files = input("Masukkan nama file (pisahkan dengan koma): ").strip().split(",")
            send_files([f.strip() for f in files])
        elif choice == "2":
            files = input("Masukkan nama file yang ingin diunduh (pisahkan dengan koma): ").strip().split(",")
            receive_files([f.strip() for f in files])
        elif choice == "3":
            print("Keluar...")
            break
        else:
            print("Pilihan tidak valid. Coba lagi.")

if __name__ == "__main__":
    menu()
    print("Program selesai.")