import shodan
import socket

# Replace 'YOUR_API_KEY' with your actual Shodan API key
SHODAN_API_KEY = "SHODAN_API_KEY"

# Initialize the Shodan API
api = shodan.Shodan(SHODAN_API_KEY)
        
# Code created by White Rabbit Neo . ai
# Version: 1.0
# Date: 2023-06-20
# All of the below functions were created by my ai friend found at this webserver:
# https://www.whiterabbitneo.com/

# Please note that the code provided here is for educational purposes
# and should only be used with permission and on systems that you own or
# have explicit permission to test.

def backdoor_finder():
    # Define the services to search for
    services = [
        "TeamViewer",
        "AnyDesk",
        "LogMeIn Hamachi",
        "Deep Instinct Agent (DIA)",
        "JumpCloud",
        "Pulse Secure Access",
        "Microsoft Remote Desktop (RDS)",
        "SolarWinds Orion",
        "RemotePC (Reveal)",
        "Citrix Workspace App"
    ]

    for service in services:
        try:
            # Perform the search query
            results = api.search(f"{service}")
            
            print(f"Total results for {service}: {results['total']}")
            
            # Iterate over the results and print the IP addresses
            for result in results['matches']:
                print(f"IP: {result['ip_str']}")
            
        except shodan.APIError as e:
            print(f"Error: {e}")    
        
def fingerprint_os(ip_address):
    try:
        # Perform a Shodan host search
        host = api.host(ip_address)
        # Extract the operating system information
        os_info = host.get('os', 'Unknown')
        return os_info
    except shodan.APIError as e:
        print(f"Error: {e}")
        return None

def search_webcams(query):
    try:
        # Perform a Shodan search
        results = api.search(query)
        return results
    except shodan.APIError as e:
        print(f"Error: {e}")
        return None

def portscan():
    # Specify the host to scan
    host = input('Host to portscan: ')

    # Perform a host search
    results = api.host(host)

    # Get the list of open ports
    open_ports = results['ports']

    # Print the open ports
    print(f"Open ports for {host}:")
    for port in open_ports:
        print(f"- {port}")

    # Perform a port scan
    for port in open_ports:
        try:
            # Create a socket and connect to the specified host and port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            
            # Check if the port is open
            if result == 0:
                print(f"Port {port} is open")
            else:
                print(f"Port {port} is closed")
            
            # Close the socket
            sock.close()
        except socket.error:
            print(f"Error connecting to port {port}")

def eduandgov_searches():
    # Define the domains to scan
    domains = [".gov", ".edu"]

    for domain in domains:
        try:
            # Perform the search query
            results = api.search(f"port:443 {domain}")
            
            print(f"Total results for 443 {domain}:  {results['total']}")
            
            # Iterate over the results and print only verified exploits
            for result in results['matches']:
                if 'vulns' in result:
                    vulns = [v for v in result['vulns'].keys() if not v.startswith('Not Verified')]
                    if vulns:
                        print(f"IP:  {result['ip_str']}")
                        print(f"Vulnerabilities (verified):\n{vulns}")
                else:
                    print("No verified vulnerabilities found.")
                
        except shodan.APIError as e:
            print(f"Error:  {e}")



def shodan_search():
    
    query = input("Enter your search query (e.g., 'cve_2022_0778'): ")

    # Exploit execution:
    # python exploit.py --url http://129.226.145.57:5000/#/signin/password --command "whoami"

    try:
        # Search for exploits using the Shodan API
        results = api.search(query)
    #    results = api.search(query, facets=[('verified', True)])


        # Print the number of results found
        print(f"Total results found: {results['total']}")

        # Iterate over the results
        for result in results['matches']:
            # Extract the IP address, port, and exploit information
            ip_address = result['ip_str']
            port = result['port']
            exploit = result.get('vulns')  # Use the `get()` method to safely access the 'vulns' key

            # Print the exploit information
            print(f"IP Address: {ip_address}")
            print(f"Port: {port}")
            print(f"Exploit: {exploit}")
            print("-------------------")

    except shodan.APIError as e:
        print(f"Error: {e}")

def main_menu():
    print("Welcome to ShodanScan tool!")
    print("Please select an option:")
    print("1. Exploit Search")
    print("2. Gov and Edu Scan")
    print("3. Port Scan")
    print("4. OS Fingerprint")
    print("5. Webcam Search")
    print("6. Backdoor Finder")
    print("7. Quit")

    choice = input("Enter your choice (1-7): ")

    if choice == '1':
        shodan_search()
    elif choice == '2':
        eduandgov_searches()
    elif choice == '3':
        portscan()
    elif choice == '4':
        ip_address = input('Enter the IP address to fingerprint: ')
        try:
            os_info = fingerprint_os(ip_address)
            print(f"Operating System: {os_info}")
        except Exception as e:
            print(f"Error: {e}")
    elif choice == '5':
        query = 'has_screenshot:true'  # Search for devices with screenshots
        try:
            results = search_webcams(query)
            if results:
                print(f"Total results: {results['total']}")
                for result in results['matches']:
                    print(f"IP: {result['ip_str']}")
                    print(f"Port: {result['port']}")
                    print(f"Hostnames: {result['hostnames']}")
                    print(f"Organization: {result['org']}")
                    print(f"Location: {result['location']}")
                    print('---')
            else:
                print("No webcam feeds found.")
        except Exception as e:
            print(f"Error: {e}")
    elif choice == '6':
        backdoor_finder()
    elif choice == '7':
        print("Exiting ShodanScan tool.")
        exit()
    else:
        print("Invalid choice. Please try again.")
        main_menu()

# Run the main menu
main_menu()