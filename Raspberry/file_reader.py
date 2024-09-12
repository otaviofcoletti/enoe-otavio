import json
import os
import time
import glob
import datetime
import logging
import sys
import psutil
import MQTTHandlerPublisher as mqtt

# Configuração de logging
logging.basicConfig(
    filename='./logs/reader.log',  # Nome do arquivo de log
    filemode='a',  # Modo append
    level=logging.INFO,  # Nível de logging
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato das mensagens de log
)

# Função para obter o uso de dados de I/O
def get_data_usage():
    counters = psutil.net_io_counters()
    return counters.bytes_sent, counters.bytes_recv

# Função para calcular o consumo de dados
def calculate_data_usage(start_sent, start_recv, end_sent, end_recv):
    sent = end_sent - start_sent
    recv = end_recv - start_recv
    return sent, recv

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

# Função genérica para verificar se arquivo está pronto para ser processado
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

# Verificar se a imagem está pronta para ser processada
def is_image_ready_for_processing(filename):
    # Por simplicidade, não verifica intervalo, apenas se o arquivo existe e não está vazio
    try:
        return os.path.getsize(filename) > 0
    except OSError as e:
        logging.error(f"Error checking image {filename}: {e}")
        return False

# Função genérica para enviar arquivo (CSV ou imagem)
def publish_data(filename, mqttc, topic):
    if os.path.getsize(filename) == 0:
        logging.info(f"File {filename} is empty, skipping...")
        try:
            os.remove(filename)
            logging.info(f"Empty file {filename} deleted.")
        except OSError as e:
            logging.error(f"Error deleting empty file {filename}: {e}")
        return

    fail_on_publish = False
    try:
        if filename.endswith(".csv"):
            with open(filename, mode='r') as file:
                lines = file.readlines()
                if len(lines) <= 1:
                    logging.info(f"File {filename} has no data (just header), skipping and deleting...")
                    os.remove(filename)
                    return
                
                for line in lines[1:]:  # Skip header
                    try:
                        json_data = json.dumps(line.strip().split(','))
                        result = mqttc.client.publish(topic, json_data, qos=1)
                        result.wait_for_publish()
                        logging.info(f"Publishing {filename} {line}")
                    except Exception as e:
                        fail_on_publish = True
                        logging.error(f"Error publishing message ultrasonic: {e}")
        
        elif filename.endswith(".jpg") or filename.endswith(".png"):
            with open(filename, 'rb') as image_file:
                image_data = image_file.read()
                try:
                    result = mqttc.client.publish(topic, image_data, qos=1)
                    result.wait_for_publish()
                    logging.info(f"Publishing {filename}")
                except Exception as e:
                    fail_on_publish = True
                    logging.error(f"Error publishing message image: {e}")
        
        # Apagar o arquivo após envio
        try:
            if not fail_on_publish:
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

    # Obter contadores iniciais de I/O
    start_sent, start_recv = get_data_usage()

    while True:
        # Encontrar arquivos CSV para processar
        try:
            for filename in glob.glob("data_ultrassonic/readings_*.csv"):
                if is_ready_for_processing(filename, csv_file_creation_seconds):
                    publish_data(filename, mqttc, "ultrassonic")
                else:
                    logging.info(f"File {filename} is not ready for processing yet.")
        except Exception as e:
            logging.error(f"Error processing files: {e}")

        # Encontrar imagens para processar
        try:
            for filename in glob.glob("data_image/*.jpg"):
                if is_image_ready_for_processing(filename):
                    publish_data(filename, mqttc, "image")
                else:
                    logging.info(f"Image {filename} is not ready for processing yet.")
        except Exception as e:
            logging.error(f"Error processing images: {e}")

        # Calcular e registrar o consumo de dados
        end_sent, end_recv = get_data_usage()
        sent, recv = calculate_data_usage(start_sent, start_recv, end_sent, end_recv)
        logging.info(f"Data sent: {sent / 1024:.2f} KB")
        logging.info(f"Data received: {recv / 1024:.2f} KB")
        logging.info(f"Total data usage: {(sent + recv) / 1024:.2f} KB")

        # Atualizar contadores
        start_sent, start_recv = end_sent, end_recv

        time.sleep(60)  # Esperar antes de verificar novos arquivos

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Program interrupted by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
