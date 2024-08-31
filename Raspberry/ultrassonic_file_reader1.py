import paho.mqtt.client as mqtt
import json
import os
import time
import glob
import signal
import psutil
import subprocess
import requests
import logging
import sys
import datetime

# Carregar as configurações do arquivo config.json
try:
    with open("config.json") as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading config file: {e}")
    exit(1)

mqtt_config = config["MQTT"]
broker_endpoint = mqtt_config["broker_endpoint"]
port = mqtt_config["port"]

credentials_config = config["CREDENTIALS"]
username = credentials_config["username"]
password = credentials_config["password"]

config_csv_interval = config["CSV_INTERVALS"]
csv_file_creation_minutes = config_csv_interval["file_creation_minutes"]
csv_file_creation_seconds = csv_file_creation_minutes * 60

MAX_RETRIES = 5  # Número máximo de tentativas de reconexão
RETRY_WAIT_TIME = 10  # Tempo de espera entre as tentativas (segundos)

def on_publish(client, userdata, mid, reason_code, properties=None):
    print(f"Message with mid {mid} published successfully.")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to broker")
        client.connected_flag = True
    else:
        print(f"Failed to connect, return code {rc}")
        client.connected_flag = False

def kill_python3_processes():
    try:
        subprocess.run(['pkill', '-f', 'python3'], check=True)
        logging.info("Killed all Python3 processes.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to kill Python3 processes: {e}")

def set_client(server, port, username, password):
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_publish = on_publish
    mqttc.on_connect = on_connect
    mqttc.username_pw_set(username, password)  # Configurar credenciais
    mqttc.connected_flag = False
    
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            mqttc.connect(server, port=port)
            mqttc.loop_start()
            return mqttc
        except Exception as e:
            print(f"Failed to connect to MQTT broker (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            attempt += 1
            time.sleep(RETRY_WAIT_TIME)
    
    print("Maximum connection attempts reached. Killing all Python processes.")
    kill_python3_processes()

def publish_file(filename, mqttc):
    # Verificar se o arquivo está vazio
    if os.path.getsize(filename) == 0:
        print(f"File {filename} is empty, skipping...")
        try:
            os.remove(filename)
            print(f"Empty file {filename} deleted.")
        except OSError as e:
            print(f"Error deleting empty file {filename}: {e}")
        return

    try:
        with open(filename, mode='r') as file:
            lines = file.readlines()
            if len(lines) <= 1:
                print(f"File {filename} has no data (just header), skipping and deleting...")
                os.remove(filename)
                return
            
            for line in lines[1:]:  # Skip header
                try:
                    json_data = json.dumps(line.strip().split(','))
                    mqttc.publish("paho/test/topic", json_data, qos=2)
                except Exception as e:                    
                    print(f"Error publishing message: {e}")
                    
        # Apagar o arquivo após envio
        try:
            os.remove(filename)
        except OSError as e:
            print(f"Error deleting file {filename}: {e}")
    except OSError as e:
        print(f"Error opening file {filename}: {e}")

def is_ready_for_processing(filename, interval_seconds):
    # Extraindo timestamp do nome do arquivo
    try:
        timestamp_str = filename.split("readings_")[1].replace(".csv", "")
        file_time = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
        current_time = datetime.datetime.now()
        elapsed_time = (current_time - file_time).total_seconds()
        
        # Verifica se o tempo desde a criação do arquivo já passou o intervalo definido
        return elapsed_time >= interval_seconds
    except (IndexError, ValueError) as e:
        print(f"Error extracting timestamp from filename {filename}: {e}")
        return False

def main():
    mqttc = set_client(server=broker_endpoint, port=port, username=username, password=password)
    
    # Esperar pela conexão
    while not mqttc.connected_flag:
        print("Waiting for connection...")
        time.sleep(1)
    
    while True:
        # Encontrar arquivos CSV para processar
        try:
            for filename in glob.glob("data/readings_*.csv"):
                if is_ready_for_processing(filename, csv_file_creation_seconds):
                    print(f"Publishing {filename}")
                    publish_file(filename, mqttc)
                else:
                    print(f"File {filename} is not ready for processing yet.")
        except Exception as e:
            print(f"Error processing files: {e}")
        
        time.sleep(60)  # Esperar antes de verificar novos arquivos

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        kill_python3_processes()
