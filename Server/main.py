import json
from MQTTHandlerSubscriber import MQTTHandlerSubscriber
from DatabaseHandler import DatabaseHandler
import time
import base64
import os
from datetime import datetime

def load_config():
    with open("config.json") as f:
        return json.load(f)

def create_directory_structure(base_path, timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    year = date_time.year
    month = date_time.month
    day = date_time.day

    month_path = os.path.join(base_path, str(year), str(month))
    day_path = os.path.join(month_path, str(day))

    if not os.path.exists(day_path):
        os.makedirs(day_path)

    return day_path

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
    
    base_image_path = "images"

    while True:
        if not mqtt_handler.queue.empty():
            message_data = mqtt_handler.queue.get()
            topic = message_data['topic']
            message = message_data['message']
            print(f"Processing message from topic {topic}: {message}")

            if topic == 'ultrassonic':
                # Supondo que a mensagem seja um JSON com os campos 'epoch' e 'distance'
                try:
                    json_data = json.loads(message)
                    timestamp, hostname, distance, epoch = json_data

                    db_handler.insert_data(epoch, distance)
                except Exception as e:
                    print(f"Error processing message: {e}")

            elif topic == 'image':
                # Supondo que a mensagem seja um JSON com os campos 'filename' e 'image_data'
                try:
                    json_data = json.loads(message)
                    filename = json_data['filename']
                    image_data = json_data['image']

                    image_data = base64.b64decode(image_data)

                    # Extrair timestamp do nome do arquivo
                    timestamp_str = filename.split('_')[0]
                    timestamp = datetime.strptime(timestamp_str, '%d-%m-%Y').timestamp()

                    # Criar estrutura de diretórios
                    day_path = create_directory_structure(base_image_path, timestamp)

                    # Salvar a imagem em um arquivo
                    file_path = os.path.join(day_path, filename)
                    with open(file_path, 'wb') as file:
                        file.write(image_data)
                except Exception as e:
                    print(f"Error processing message: {e}")
    
        time.sleep(1)


if __name__ == "__main__":
    main()
