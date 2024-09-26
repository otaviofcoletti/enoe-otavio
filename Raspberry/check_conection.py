
import os
import sys
import subprocess
import requests
import time

import RPi.GPIO as GPIO

def check_connection(url):
    try:
        requests.get(url, timeout=5)
        return True
    except requests.exceptions.RequestException:
        return False

def kill_python3_processes():
    os.system('pkill -f python3')

def relay_on():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    GPIO.output(17, GPIO.LOW)

    time.sleep(3)

    GPIO.output(17, GPIO.HIGH)
    GPIO.cleanup()




def main():
    faults = 0
    url = "https://www.google.com"
    while True:
        if not check_connection(url):
            
            #kill_python3_processes()
            time.sleep(240)
            if not check_connection(url):
                print("Rebooting 4G")
                relay_on()
                print("Connection lost. Killing all Python3 processes...")
                kill_python3_processes()
           

            
            # The script will continue checking the connection indefinitely
        
        time.sleep(120) # Check the connection every 60 seconds.
        




if __name__ == "__main__":
    main()

