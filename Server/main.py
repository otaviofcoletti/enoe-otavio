
import json
from MQTTHandlerSubscriber import MQTTHandlerSubscriber
from DatabaseHandler import DatabaseHandler
import time

def load_config():
    with open("config.json") as f:
        return json.load(f)

def main():
    config = load_config()

    mqtt_config = config["MQTT"]
    broker_endpoint = mqtt_config["broker_endpoint"]
    topic = "paho/test/topic"

    db_config = config["DATABASE"]

    username = config["CREDENTIALS"]["username"]
    password = config["CREDENTIALS"]["password"]

    db_handler = DatabaseHandler(db_config)
    mqtt_handler = MQTTHandlerSubscriber(broker_endpoint, port=1883, username=username, password=password)


    mqtt_handler.connect()
    mqtt_handler.subscribe(topic)  # Subscrever ao tópico
    
    db_handler.connect()
    
    while True:
        if not mqtt_handler.queue.empty():
            message_data = mqtt_handler.queue.get()
            topic = message_data['topic']
            message = message_data['message']
            print(f"Processing message from topic {topic}: {message}")
    
            # Supondo que a mensagem seja um JSON com os campos 'epoch' e 'distance'
            try:
                json_data = json.loads(message)
                timestamp, hostname, distance, epoch = json_data

                db_handler.insert_data(epoch, distance)
            except Exception as e:
                print(f"Error processing message: {e}")
    
        time.sleep(1)


if __name__ == "__main__":
    main()
