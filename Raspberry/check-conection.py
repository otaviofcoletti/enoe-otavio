import os
import sys
import subprocess
import requests
import time

def check_connection(url):
    try:
        requests.get(url, timeout=5)
        return True
    except requests.exceptions.RequestException:
        return False

def kill_python3_processes():
    os.system('pkill -f python3')

def restart_wifi():
    os.system('sudo ifconfig wlan0 down')
    time.sleep(5)
    os.system('sudo ifconfig wlan0 up')

def main():
    url = "https://www.google.com"
    while True:
        if not check_connection(url):
            time.sleep(240)
            if not check_connection(url):
                print("Rebooting Wi-Fi")
                restart_wifi()
                print("Connection lost. Killing all Python3 processes...")
                kill_python3_processes()
        
        time.sleep(120) # Check the connection every 120 seconds.

if __name__ == "__main__":
    main()
