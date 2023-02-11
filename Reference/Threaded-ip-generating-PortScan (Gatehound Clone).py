import socket
import threading
import random

def scan_port(host, port, semaphore):
    global oct1
    global oct2
    global oct3
    global oct4
    global portNum
    global chStart
    oct1 = random.randint(20,120)
    oct2 = random.randint(1,255)
    oct3 = random.randint(1,255)
    oct4 = random.randint(1,255)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ipGen = '%s.%s.%s.%s' % (oct1, oct2, oct3, oct4)
    print ("Scanning port %s on host %s.\n" % (port,ipGen))
    s.settimeout(1)
    try:
        connection = s.connect((ipGen, port))
        inp = input("press enter to continue - host %s\n" % (ipGen))
        print('Port {port} is open')
        connection.close()
    except:
        pass
    finally:
        semaphore.release()

def main(host):
    semaphore = threading.Semaphore(10)
    threads = []
    for num_port in range(90000):
        semaphore.acquire()
        t = threading.Thread(target=scan_port, args=(host, port, semaphore))
        threads.append(t)
        t.start()

if __name__ == '__main__':
    host = "host"
    port = int(input('Enter the port for scanning: '))
    main(host)
