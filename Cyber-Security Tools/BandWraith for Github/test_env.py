# This miniature UDP Server hosting environment, enables you to test your DDoSer against it with a quick disconnect upon targetting it.

# Feel free to use your loopback address 127.0.0.1 on port 1345.
# And watch the disconnect happen instantly after running the script.

### Test Results below:
 # UDP server up and listening on 127.0.0.1:1345
 # Traceback (most recent call last):
 # File "C:\Users\Admin\Desktop\test_env.py", line 20, in <module>
 #   start_udp_server(HOST_IP, HOST_PORT)
 # File "C:\Users\Admin\Desktop\test_env.py", line 10, in start_udp_server
 #   data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
 #                ^^^^^^^^^^^^^^^^^^^
#ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
###

import socket

def start_udp_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.bind((ip, port))
    print(f"UDP server up and listening on {ip}:{port}")

    try:
        while True:
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            print(f"Received message: {data} from {addr}")
    except KeyboardInterrupt:
        print("UDP server is closing")
    finally:
        sock.close()

if __name__ == "__main__":
    HOST_IP = "127.0.0.1"  # Listen on localhost
    HOST_PORT = 1345       # Example port
    start_udp_server(HOST_IP, HOST_PORT)
