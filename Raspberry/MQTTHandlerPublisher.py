import paho.mqtt.client as mqtt
import json
import sys
import time
import logging

logger = logging.getLogger('MQTTHandlerPublisher')
logger.setLevel(logging.INFO)

handler = logging.FileHandler('./logs/MQTTHandlerPublisher.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class MQTTHandlerPublisher:
    def __init__(self, broker_address, port, username=None, password=None, MAX_RETRIES=5, RETRY_WAIT_TIME=10):
        self.client = mqtt.Client(protocol=mqtt.MQTTv5)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.connected_flag = False

        self.MAX_RETRIES = MAX_RETRIES
        self.RETRY_WAIT_TIME = RETRY_WAIT_TIME
        self.port = port
        self.broker_address = broker_address

        # Configurar credenciais se fornecidas
        if username and password:
            self.client.username_pw_set(username, password)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("Connected to broker")
            client.connected_flag = True
        else:
            logger.error(f"Failed to connect, return code {rc}")
            client.connected_flag = False

    def on_publish(self, client, userdata, mid, reason_code=None, properties=None):
        logger.info(f"Message with mid {mid} published successfully.")

    def connect(self):
        attempt = 0 
        while attempt < self.MAX_RETRIES:
            try:
                self.client.connect(self.broker_address, port=self.port, clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY)
                self.client.loop_start()  # Start the network loop
                return  # Exit the method if successful
            except Exception as e:
                logger.error(f"Failed to connect to MQTT broker (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                attempt += 1
                time.sleep(self.RETRY_WAIT_TIME)

        logger.error("Maximum connection attempts reached. Exiting....")
        sys.exit(1)  # Encerra o programa com código de status 1 (erro)


    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()  # Parar o loop da rede
        logger.info("Disconected")