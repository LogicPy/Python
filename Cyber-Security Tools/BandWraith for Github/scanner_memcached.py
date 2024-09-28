import socket
import threading
import random
import struct

def scan_port(host, port, semaphore):
    # Generate a random IP address
    ipGen = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
    
    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)  # Set timeout for receiving a response

    # Define the payload
    payload = b"\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"

    try:
        # Send the payload to the randomly generated IP address on the specified port
        s.sendto(payload, (ipGen, port))
        #print(f"Sent payload to {ipGen}:{port}")

        # Wait for a response
        try:
            data, addr = s.recvfrom(1024)
            print(f"Received response from {addr}: {data.decode()}")
            enter = input('Press enter to continue scan...')
        except socket.timeout:
            #print(f"Timeout waiting for a response from {ipGen}:{port}")
            pass
    except Exception as e:
        print(f"Failed to send payload to {ipGen}:{port}, error: {e}")
    finally:
        s.close()
        semaphore.release()

def main():
    port = int(input('Enter the port for scanning (e.g., 11211 for Memcached): '))
    semaphore = threading.Semaphore(10)  # Control number of concurrent threads
    threads = []

    for _ in range(10000):  # Limiting to 100 for testing; adjust as needed
        semaphore.acquire()
        t = threading.Thread(target=scan_port, args=("host", port, semaphore))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()
