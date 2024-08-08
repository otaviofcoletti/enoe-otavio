import paho.mqtt.client as mqtt
import time

class MQTTClientHandler:
    def __init__(self, broker_address, topic):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe
        
        self.client.user_data_set([])  # Inicializando userdata como uma lista
        self.broker_address = broker_address
        self.topic = topic

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
        userdata.append(message.payload)
        # Uncomment the following lines if you want to unsubscribe after receiving 10 messages
        # if len(userdata) >= 10:
        #     client.unsubscribe(self.topic)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
        else:
            client.subscribe(self.topic)

    def connect_and_listen(self):
        self.client.connect(self.broker_address)
        self.client.loop_forever()

    def get_received_messages(self):
        return self.client.user_data_get()

if __name__ == "__main__":
    broker_address = "mqtt.eclipseprojects.io"
    topic = "paho/test/topic"

    mqtt_handler = MQTTClientHandler(broker_address, topic)
    
    try:
        mqtt_handler.connect_and_listen()
    except KeyboardInterrupt:
        print("Interrupted by user.")
        mqtt_handler.client.disconnect()
    
    received_messages = mqtt_handler.get_received_messages()
    print(f"Received the following messages: {received_messages}")
