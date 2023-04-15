import socket
import struct
import random
from tqdm import tqdm

services = {
    'TeamViewer': [5938],
    'AnyDesk': [7070],
    'RemotePC': [8000],
    'Splashtop Business Access': [443, 8443],
    'Zoho Assist': [80, 443],
    'ConnectWise Control': [80, 443, 8040, 8041, 8042],
    'BeyondTrust Remote Support': [80, 443, 3443],
    'GoTo Resolve': [80, 443, 8200, 8201]
}

def scan(ip):
    # generate a random port number
    port = random.choice(list(services.values()))[0]
    # create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        # connect to the service on the specified port
        sock.connect((ip, port))
        # print the service and port number if a connection is successful
        print(ip + ": " + list(services.keys())[list(services.values()).index([port])])
    except:
        pass
    sock.close()

# generate a random IP address and scan it for each service
while(True):
    for i in tqdm(range(10)):
        ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        scan(ip)
