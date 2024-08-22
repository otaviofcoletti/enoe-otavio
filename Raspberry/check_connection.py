import os
import subprocess
import requests
import time
import logging
import sys

# Configure logging
logging.basicConfig(filename='connection_monitor.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def check_connection(url):
    try:
        requests.get(url, timeout=5)
        return True
    except requests.exceptions.RequestException as e:
        logging.warning(f"Connection check failed: {e}")
        return False

def kill_python3_processes():
    try:
        subprocess.run(['pkill', '-f', 'python3'], check=True)
        logging.info("Killed all Python3 processes.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to kill Python3 processes: {e}")

def restart_wifi():
    try:
        subprocess.run(['sudo', 'ifconfig', 'wlan0', 'down'], check=True)
        time.sleep(5)
        subprocess.run(['sudo', 'ifconfig', 'wlan0', 'up'], check=True)
        logging.info("Wi-Fi interface wlan0 restarted.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to restart Wi-Fi: {e}")

def main():
    url = "https://www.google.com"
    retry_interval = 120
    retries = 0
    max_retries = 3
    
    try:
        while True:
            if not check_connection(url):
                retries += 1
                time.sleep(retry_interval)

                if retries >= max_retries:
                    logging.warning("Connection lost. Rebooting Wi-Fi.")
                    restart_wifi()
                    logging.warning("Killing all Python3 processes...")
                    kill_python3_processes()
                    retries = 0  # Reset retries after handling

            else:
                retries = 0  # Reset retries if connection is successful
            
            time.sleep(retry_interval)

    except KeyboardInterrupt:
        logging.info("Script terminated by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
