import json
import os
import time
import glob
import datetime
import logging
import sys

import MQTTHandlerPublisher as mqtt

# Configuração de logging
logging.basicConfig(
    filename='./logs/reader.log',  # Nome do arquivo de log
    filemode='a',  # Modo append
    level=logging.INFO,  # Nível de logging
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato das mensagens de log
)

# Carregar as configurações do arquivo config.json
try:
    with open("config.json") as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error(f"Error loading config file: {e}")
    sys.exit(1)

mqtt_config = config["MQTT"]
broker_endpoint = mqtt_config["broker_endpoint"]
port = mqtt_config["port"]

credentials_config = config["CREDENTIALS"]
username = credentials_config["username"]
password = credentials_config["password"]

config_csv_interval = config["CSV_INTERVALS"]
csv_file_creation_minutes = config_csv_interval["file_creation_minutes"]
csv_file_creation_seconds = csv_file_creation_minutes * 60

def is_ready_for_processing(filename, interval_seconds):
    try:
        timestamp_str = filename.split("readings_")[1].replace(".csv", "")
        file_time = datetime.datetime.strptime(timestamp_str, '%d-%m-%Y_%H:%M:%S')
        current_time = datetime.datetime.now()
        elapsed_time = (current_time - file_time).total_seconds()
        return elapsed_time >= interval_seconds
    except (IndexError, ValueError) as e:
        logging.error(f"Error extracting timestamp from filename {filename}: {e}")
        return False

def publish_file(filename, mqttc):
    if os.path.getsize(filename) == 0:
        logging.info(f"File {filename} is empty, skipping...")
        try:
            os.remove(filename)
            logging.info(f"Empty file {filename} deleted.")
        except OSError as e:
            logging.error(f"Error deleting empty file {filename}: {e}")
        return

    try:
        with open(filename, mode='r') as file:
            lines = file.readlines()
            if len(lines) <= 1:
                logging.info(f"File {filename} has no data (just header), skipping and deleting...")
                os.remove(filename)
                return
            
            for line in lines[1:]:  # Skip header
                try:
                    json_data = json.dumps(line.strip().split(','))
                    mqttc.client.publish("paho/test/topic", json_data, qos=1)
                except Exception as e:
                    logging.error(f"Error publishing message: {e}")
                    
        # Apagar o arquivo após envio
        try:
            os.remove(filename)
        except OSError as e:
            logging.error(f"Error deleting file {filename}: {e}")
    except OSError as e:
        logging.error(f"Error opening file {filename}: {e}")

def main():
    mqttc = mqtt.MQTTHandlerPublisher(broker_address=broker_endpoint, port=port, username=username, password=password)

    mqttc.connect()
    # Esperar pela conexão
    while not mqttc.client.connected_flag:
        logging.info("Waiting for connection...")
        time.sleep(1)

    while True:
        # Encontrar arquivos CSV para processar
        try:
            for filename in glob.glob("data/readings_*.csv"):
                if is_ready_for_processing(filename, csv_file_creation_seconds):
                    logging.info(f"Publishing {filename}")
                    publish_file(filename, mqttc)
                else:
                    logging.info(f"File {filename} is not ready for processing yet.")
        except Exception as e:
            logging.error(f"Error processing files: {e}")
        
        time.sleep(60)  # Esperar antes de verificar novos arquivos

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Program interrupted by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
