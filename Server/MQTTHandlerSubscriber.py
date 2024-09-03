import paho.mqtt.client as mqtt
import json
import sys
import time
from queue import Queue
import logging
import os

class MQTTHandlerSubscriber:
    def __init__(self, broker_address, port, username=None, password=None, MAX_RETRIES=5, RETRY_WAIT_TIME=10, log_file='logs/subscriber.log', append_log=True):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message  # Usa a função de callback para tratar as mensagens recebidas
        self.client.connected_flag = False

        self.MAX_RETRIES = MAX_RETRIES
        self.RETRY_WAIT_TIME = RETRY_WAIT_TIME
        self.port = port
        self.broker_address = broker_address

        self.queue = Queue()

        # Configurar credenciais se fornecidas
        if username and password:
            self.client.username_pw_set(username, password)

        # Configurar logging
        self.setup_logging(log_file, append_log)

    def setup_logging(self, log_file, append_log):
        # Verificar se o diretório de logs existe
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_mode = 'a' if append_log else 'w'
        logging.basicConfig(filename=log_file, filemode=log_mode, level=logging.DEBUG,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.info("Logging is set up.")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.logger.info("Connected to broker")
            client.connected_flag = True
        else:
            self.logger.error(f"Failed to connect, return code {rc}")
            client.connected_flag = False

    def connect(self):
        attempt = 0
        while attempt < self.MAX_RETRIES:
            try:
                self.client.connect(self.broker_address, port=self.port)
                self.client.loop_start()  # Start the network loop
                self.logger.info("Successfully connected to MQTT broker")
                return  # Exit the method if successful
            except Exception as e:
                self.logger.error(f"Failed to connect to MQTT broker (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                attempt += 1
                time.sleep(self.RETRY_WAIT_TIME)

        self.logger.critical("Maximum connection attempts reached. Exiting....")
        sys.exit(1)  # Encerra o programa com código de status 1 (erro)

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()  # Parar o loop da rede
        self.logger.info("Disconnected from MQTT broker")

    def on_message(self, client, userdata, message):
        self.logger.info(f"Received message on topic {message.topic}: {message.payload.decode('utf-8')}")

        # Criar um dicionário com o tópico e a mensagem
        message_data = {
            'topic': message.topic,
            'message': message.payload.decode('utf-8')
        }

        # Adicionar o dicionário à fila
        self.queue.put(message_data)
        self.logger.debug(f"Message added to queue: {message_data}")

    def subscribe(self, topic):
        try:
            self.client.subscribe(topic)
            self.logger.info(f"Subscribed to topic: {topic}")
        except Exception as e:
            self.logger.error(f"Failed to subscribe to topic {topic}: {e}")
