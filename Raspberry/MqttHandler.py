import paho.mqtt.client as mqtt
import json

class MQTTClientHandler:
    def __init__(self, broker_address, topic, username=None, password=None):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe
        self.client.on_publish = self.on_publish

        self.client.user_data_set([])  # Inicializando userdata como uma lista
        self.broker_address = broker_address
        self.topic = topic
        
        # Configurar credenciais se fornecidas
        if username and password:
            self.client.username_pw_set(username, password)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"Failed to connect: {reason_code}. Retrying...")
        else:
            client.subscribe(self.topic)

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        if reason_code_list[0].is_failure:
            print(f"Broker rejected your subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
        if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
            print("Unsubscribe succeeded.")
        else:
            print(f"Broker replied with failure: {reason_code_list[0]}")
        client.disconnect()
    
    def on_publish(client, userdata, mid, reason_code, properties=None):
        try:
            userdata.remove(mid)
        except KeyError:
            print(f"Could not publish, MID not found: {mid}")

    def on_message(self, client, userdata, message):
        print(f"Received message: {message.payload.decode('utf-8')}")
        userdata.append(message.payload.decode('utf-8'))

        try:
            # Assumindo que o payload é uma lista, convertendo para uma lista Python
            json_data = json.loads(message.payload.decode('utf-8'))
            timestamp, hostname, distance, epoch = json_data

            # Inserir a mensagem no banco de dados
            self.db_handler.insert_data(epoch, distance)
        except Exception as e:
            print(f"Error processing message: {e}")



    def connect_and_listen(self):
        self.client.connect(self.broker_address)
        self.client.loop_forever()

    def get_received_messages(self):
        return self.client.user_data_get()

    def disconnect(self):
        self.client.disconnect()