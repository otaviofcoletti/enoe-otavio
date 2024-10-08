import json
import os
import time
import glob
import datetime
import sys
import psutil
import MQTTHandlerPublisher as mqtt
import base64
from RaspberrySystemInfo import RaspberrySystemInfo

import subprocess
import requests

import RPi.GPIO as GPIO
from LoggingClass import Logger  # Certifique-se de que o caminho para a classe Logger está correto



logger = Logger('file_consumer', rotation='W0').get_logger()  # Rotação semanal


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
    logger.error(f"Error loading config file: {e}")
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

raspberry_config = config['RASPBERRY']
raspberry_info_interval_minutes = raspberry_config['info_interval_minutes']
raspberry_info_interval_seconds = raspberry_info_interval_minutes * 60

# Função genérica para verificar se arquivo está pronto para ser processado
def is_ready_for_processing(filename, interval_seconds):
    try:
        timestamp_str = filename.split("readings_")[1].replace(".csv", "")
        file_time = datetime.datetime.strptime(timestamp_str, '%d-%m-%Y_%H:%M:%S')
        current_time = datetime.datetime.now()
        elapsed_time = (current_time - file_time).total_seconds()
        return elapsed_time >= interval_seconds
    except (IndexError, ValueError) as e:
        logger.error(f"Error extracting timestamp from filename {filename}: {e}")
        return False

# Verificar se a imagem está pronta para ser processada
def is_image_ready_for_processing(filename, wait_time=2):
    try:
        initial_size = os.path.getsize(filename)
        time.sleep(wait_time)  # Espera um tempo para ver se o arquivo ainda está sendo escrito
        final_size = os.path.getsize(filename)
        
        if initial_size > 0 and initial_size == final_size:
            return True
        else:
            logger.debug(f"Image {filename} is still being written, skipping for now.")
            return False
    except OSError as e:
        logger.error(f"Error checking image {filename}: {e}")
        return False

def relay_on():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    GPIO.output(17, GPIO.LOW)
    logger.info(f"GPIO Low...")
    time.sleep(3)
    GPIO.output(17, GPIO.HIGH)
    logger.info(f"GPIO High...")

    GPIO.cleanup()


# Função genérica para enviar arquivo (CSV ou imagem)
def publish_data(filename, mqttc, topic):
    if os.path.getsize(filename) == 0:
        logger.debug(f"File {filename} is empty, skipping...")
        try:
            os.remove(filename)
            logger.debug(f"Empty file {filename} deleted.")
        except OSError as e:
            logger.error(f"Error deleting empty file {filename}: {e}")
        return

    fail_on_publish = False
    try:
        if filename.endswith(".csv"):
            with open(filename, mode='r') as file:
                lines = file.readlines()
                if len(lines) <= 1:
                    logger.debug(f"File {filename} has no data (just header), skipping and deleting...")
                    os.remove(filename)
                    return
                
                for line in lines[1:]:  # Skip header
                    try:
                        json_data = json.dumps(line.strip().split(','))
                        result = mqttc.client.publish(topic, json_data, qos=1)
                        result.wait_for_publish(timeout=100)
                        logger.info(f"Publishing {filename}")

                    except Exception as e:
                        relay_on()
                        fail_on_publish = True
                        logger.error(f"Error publishing message ultrasonic: {e}")
        
        elif filename.endswith(".jpg") or filename.endswith(".png"):
            with open(filename, 'rb') as image_file:
                image_data = image_file.read()
                # Converta os dados da imagem para base64 para enviá-los via JSON
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                message = {
                    "filename": os.path.basename(filename),
                    "encoded_image": encoded_image
                }
                json_message = json.dumps(message)
                
                try:
                    result = mqttc.client.publish(topic, json_message, qos=1)
                    result.wait_for_publish(timeout=100)
                    logger.info(f"Publishing {filename}")
                except Exception as e:
                    relay_on()
                    fail_on_publish = True
                    logger.error(f"Error publishing message image: {e}")
        
        # Apagar o arquivo após envio
        try:
            if not fail_on_publish:
                os.remove(filename)
        except OSError as e:
            logger.error(f"Error deleting file {filename}: {e}")
    except OSError as e:
        logger.error(f"Error opening file {filename}: {e}")
        





def main():
    """
    Função principal para gerenciar a conexão MQTT e processar arquivos.

    Esta função realiza as seguintes tarefas:
    1. Conecta-se ao broker MQTT.
    2. Aguarda a conexão ser estabelecida.
    3. Verifica continuamente arquivos CSV e imagens para processar.
    4. Publica dados de arquivos CSV e imagens no broker MQTT.
    5. Registra estatísticas de uso de dados.

    A função trata exceções que podem ocorrer durante o processamento de arquivos e registra mensagens de erro apropriadas.

    Nota:
        - A função assume a existência de várias funções auxiliares, como `get_data_usage`, 
          `is_ready_for_processing`, `publish_data`, `calculate_data_usage` e `is_image_ready_for_processing`.
        - A função usa um logger para registrar informações e erros.
        - A função inclui um intervalo de espera antes de verificar novos arquivos.

    Levanta:
        Exception: Se ocorrer um erro durante o processamento de arquivos ou imagens.
    """

    raspberry_info = RaspberrySystemInfo()

    mqttc = mqtt.MQTTHandlerPublisher(broker_address=broker_endpoint, port=port, username=username, password=password)

    mqttc.connect()
    # Esperar pela conexão
    while not mqttc.client.connected_flag:
        logger.info("Waiting for connection...")
        time.sleep(1)

    # Obter contadores iniciais de I/O
    # start_sent, start_recv = get_data_usage()
    last_raspberry_info_time = datetime.datetime.now()

    while True:
        # Encontrar arquivos CSV para processar
        try:
            for filename in glob.glob("data_ultrassonic/readings_*.csv"):
                if is_ready_for_processing(filename, csv_file_creation_seconds):
                    start_sent, start_recv = get_data_usage()
                    publish_data(filename, mqttc, "ultrassonic")
                    # end_sent, end_recv = get_data_usage()
                    # sent, recv = calculate_data_usage(start_sent, start_recv, end_sent, end_recv)
                    # logger.info(f"Data sent: {sent / 1024:.2f} KB")
                    # logger.info(f"Data received: {recv / 1024:.2f} KB")
                    # logger.info(f"Total data usage: {(sent + recv) / 1024:.2f} KB")
                else:
                    #logger.info(f"File {filename} is not ready for processing yet.")
                    continue
        except Exception as e:
            logger.error(f"Error processing files: {e}")

        # Encontrar imagens para processar
        try:
            for filename in glob.glob("data_images/*.jpg"):
                if is_image_ready_for_processing(filename):
                    start_sent, start_recv = get_data_usage()
                    publish_data(filename, mqttc, "images")
                    # end_sent, end_recv = get_data_usage()
                    # sent, recv = calculate_data_usage(start_sent, start_recv, end_sent, end_recv)
                    # logger.info(f"Data sent: {sent / 1024:.2f} KB")
                    # logger.info(f"Data received: {recv / 1024:.2f} KB")
                    # logger.info(f"Total data usage: {(sent + recv) / 1024:.2f} KB")
                else:
                    #logger.info(f"Image {filename} is not ready for processing yet.")
                    continue
        except Exception as e:
            logger.error(f"Error processing images: {e}")

        try:
            current_time = datetime.datetime.now()
            elapsed_time = (current_time - last_raspberry_info_time).total_seconds()
            if elapsed_time >= raspberry_info_interval_seconds:
                mqtt_payload = raspberry_info.format_info_for_mqtt()
                result = mqttc.client.publish("raspberry_info", mqtt_payload, qos=1)
                result.wait_for_publish(timeout=100)
                logger.info(f"Publishing {mqtt_payload}")
                last_raspberry_info_time = datetime.datetime.now()
        except Exception as e:
            logger.error(f"Error sending raspberry info: {e}")

        time.sleep(1)  # Esperar antes de verificar novos arquivos

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
