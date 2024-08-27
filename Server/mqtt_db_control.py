import paho.mqtt.client as mqtt
import psycopg2
import time
import json

class MQTTClientHandler:
    def __init__(self, broker_address, topic, db_config, username=None, password=None):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe
        
        self.client.user_data_set([])  # Inicializando userdata como uma lista
        self.broker_address = broker_address
        self.topic = topic
        self.db_config = db_config
        
        # Configurar credenciais se fornecidas
        if username and password:
            self.client.username_pw_set(username, password)

        self.conn = None
        self.cursor = None

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        if reason_code_list[0].is_failure:
            print(f"Broker rejected your subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
        if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
            print("Unsubscribe succeeded (if SUBACK is received in MQTTv3 it succeeded)")
        else:
            print(f"Broker replied with failure: {reason_code_list[0]}")
        client.disconnect()

    def on_message(self, client, userdata, message):
        print(f"Received message: {message.payload.decode('utf-8')}")
        userdata.append(message.payload.decode('utf-8'))

        try:
            # Assumindo que o payload é uma lista, convertendo para uma lista Python
            json_data = json.loads(message.payload.decode('utf-8'))
            
            # Extraindo dados da lista
            timestamp, hostname, distance, epoch = json_data

            # Inserir a mensagem no banco de dados
            self.cursor.execute(
                "INSERT INTO ultrassonic (epoch, distance) VALUES (%s, %s)",
                (epoch, distance)
            )
            self.conn.commit()
            print(f"Commit done {epoch}, {distance}")
        except Exception as e:
            print(f"Error inserting data into database: {e}")
            self.conn.rollback()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
        else:
            client.subscribe(self.topic)

    def connect_db(self, max_retries=5, retry_delay=5):
        """Tentar conectar ao banco de dados com retries."""
        attempt = 0
        while attempt < max_retries:
            try:
                self.conn = psycopg2.connect(**self.db_config)
                self.cursor = self.conn.cursor()
                print("Connected to the database successfully.")
                return True
            except psycopg2.OperationalError as e:
                print(f"Failed to connect to the database (attempt {attempt + 1}/{max_retries}): {e}")
                attempt += 1
                time.sleep(retry_delay)
        print("Failed to connect to the database after multiple attempts. Exiting...")
        return False

    def connect_and_listen(self):
        self.client.connect(self.broker_address)
        self.client.loop_forever()

    def get_received_messages(self):
        return self.client.user_data_get()

    def close(self):
        # Fechar a conexão com o banco de dados
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

if __name__ == "__main__":

    with open("config.json") as f:
        config = json.load(f)

    mqtt_config = config["MQTT"]
    broker_endpoint = mqtt_config["broker_endpoint"]
    port = mqtt_config["port"]

    credentials_config = config["CREDENTIALS"]
    username = credentials_config["username"]
    password = credentials_config["password"]

    topic = "paho/test/topic"

    # Configurações do banco de dados
    db_config = {
        'dbname': 'ultrassonic_sensor',
        'user': 'user',
        'password': 'password',
        'host': '172.19.0.2',
        'port': '5432'
    }

    # Credenciais para autenticação MQTT
    username = "server"
    password = "server.publisher"

    mqtt_handler = MQTTClientHandler(broker_endpoint, topic, db_config, username, password)
    
    try:
        # Primeiro tenta conectar ao banco de dados
        if mqtt_handler.connect_db():
            mqtt_handler.connect_and_listen()
        else:
            print("Exiting due to database connection failure.")
    except KeyboardInterrupt:
        print("Interrupted by user.")
        mqtt_handler.client.disconnect()
    finally:
        mqtt_handler.close()
    
    received_messages = mqtt_handler.get_received_messages()
    print(f"Received the following messages: {received_messages}")
