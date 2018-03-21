# Wayne Kenney
# 5/3/2016
# USE (Unique String Encryption)

import os

# [?] Function for copying encrypted text to clipboard
def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)

def decr():
    # Declare input string
    x = raw_input("\nEnter Message to Decrypt: ").lower()

    # Final string
    decrypted = ""

    # For every Character in input string
    for c in x:
        # Uses Caesar cipher of -1 to every letter
        val = ord(c)-1

        # ASCII values have a limit of 255,
        # so we will simply wrap the characters around
        if val < 0:
            decrypted += chr(255-val)
        else:
            decrypted += chr(val)

    # Display encrypted Text
    print "\nYour decrypted text: %s" % (decrypted)



def encr():
    # Declare input string
    x = raw_input("\nEnter Message to Encrypt: ").lower()

    # Final string
    encrypted = ""

    # For every Character in input string
    for c in x:
        # Uses Caesar cipher of +1 to every letter
        val = ord(c)+1

        # ASCII values have a limit of 255,
        # so we will simply wrap the characters around
        if val > 255:
            encrypted += chr(val-255)
        else:
            encrypted += chr(val)

    # Display encrypted Text
    print "\nYour encrypted text: %s" % (encrypted)

    print "\nEncrypted text copied to clipboard.\n"
    # Copy text to clipboard
    addToClipBoard(encrypted)


while(True):
    
    cmd = raw_input("Enter command (? for help): ").lower()

    if cmd == "encrypt":
        encr()
    elif cmd == "decrypt":
        decr()
    elif cmd == "exit":
        exit()
    elif cmd == "?" or cmd == "help":
        print "\n Commands:\n\n encrypt\t(input for encryption)\n decrypt\t(input for decryption)\n exit\t\t(input to exit program)\n"
    else:   
        print "\n [!] Invalid command. Try again. \n"
