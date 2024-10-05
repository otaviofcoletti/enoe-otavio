import time
import json
import os
import sys
import UltrassonicClass
from LoggingClass import Logger  # Certifique-se de que o caminho para a classe Logger está correto
import MQTTHandlerPublisher as mqtt


logger = Logger('take_ultrassonic', rotation='W0').get_logger()  # Rotação semanal

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

def main():

    ultrassonic_sensor = UltrassonicClass.UltrassonicClass(serialportname = '/dev/ttyS0', baudrate = 9600)
    ultrassonic_sensor.set_serial()

    mqttc = mqtt.MQTTHandlerPublisher(broker_address=broker_endpoint, port=port, username=username, password=password)

    mqttc.connect()
    # Esperar pela conexão
    while not mqttc.client.connected_flag:
        logger.info("Waiting for connection...")
        time.sleep(1)
    
    end_time = time.time() + 60*2  # 10 minutes
    while time.time() < end_time:
                             
        time.sleep(5)
        distance = ultrassonic_sensor.get_line()
        if distance is not None:
            mqttc.publish("app/ultrassonic", distance, qos=0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
