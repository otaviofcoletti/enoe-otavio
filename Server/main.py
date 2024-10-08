import json
import os
import time
import base64
from datetime import datetime
from MQTTHandlerSubscriber import MQTTHandlerSubscriber
from DatabaseHandler import DatabaseHandler
from LoggingClass import Logger  # Import the Logger class

def load_config():
    with open("config.json") as f:
        return json.load(f)

def create_directory_structure(base_path, timestamp): # Pega o dia, mês e ano do nome da imagem e cria a estrutura de diretórios
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
    topics = ["ultrassonic", "images", "raspberry_info"]

    db_config = config["DATABASE"]

    username = config["CREDENTIALS"]["username"]
    password = config["CREDENTIALS"]["password"]

    db_handler = DatabaseHandler(db_config)
    mqtt_handler = MQTTHandlerSubscriber(broker_endpoint, port=1883, username=username, password=password)

    mqtt_handler.connect()
    for topic in topics:
        mqtt_handler.subscribe(topic)  # Subscribe to topics
    
    db_handler.connect()
    
    base_image_path = "images"

    # Configuração do logger para o DatabaseHandler usando a nova classe Logger
    main_logger = Logger('main', rotation='W0').get_logger()  # Weekly rotation

    while True:
        if not mqtt_handler.queue.empty():
            try:
                message_data = mqtt_handler.queue.get()
                topic = message_data['topic']
                message = message_data['message']
                main_logger.debug(f"Processing message from topic {topic}")
            except Exception as e:
                main_logger.error(f"Error processing message from queue: {e}")

            if topic == 'ultrassonic':
                # Assuming the message is a JSON with fields 'epoch' and 'distance'
                try:
                    json_data = json.loads(message)
                    timestamp, distance, epoch = json_data

                    db_handler.insert_data('ultrassonic',epoch, distance)
                except Exception as e:
                    main_logger.error(f"Error inserting message: {e}")

            elif topic == 'images':
                # Assuming the message is a JSON with fields 'filename' and 'image_data'
                try:
                    json_data = json.loads(message)
                    filename = json_data['filename']
                    image_data = json_data['encoded_image']

                    image_data = base64.b64decode(image_data)

                    # Extract timestamp from filename
                    timestamp_str = filename.split('_')[0]
                    timestamp = datetime.strptime(timestamp_str, '%d-%m-%Y').timestamp()

                    # Create directory structure
                    day_path = create_directory_structure(base_image_path, timestamp)

                    try:
                        # Save the image to a file
                        file_path = os.path.join(day_path, filename)
                        print(f"Saving image to {file_path}")
                        with open(file_path, 'wb') as file:
                            file.write(image_data)
                            file.flush()
                            os.fsync(file.fileno())  # Garante que o sistema operacional grave os dados no disco
                    except Exception as e:
                        main_logger.error(f"Error saving image: {e}")

                except Exception as e:
                    main_logger.error(f"Error inserting message: {e}")



                    db_handler.insert_data('images',filename, day_path)

            elif topic == 'raspberry_info':
                try:
                    json_data = json.loads(message)
                    epoch = json_data['epoch']
                    cpu_temperature = float(json_data['cpu_temperature'])
                    cpu_usage = float(json_data['cpu_usage'])
                    ram_usage = float(json_data['ram_usage'])
                    storage_usage = float(json_data['storage_usage'])
                    raspberry_data = {
                        'cpu_temperature': cpu_temperature,
                        'cpu_usage': cpu_usage,
                        'ram_usage': ram_usage,
                        'storage_usage': storage_usage
                    }
                    db_handler.insert_data('raspberry_info',epoch, raspberry_data)
                
                except Exception as e:
                    main_logger.error(f"Error inserting raspberry info: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()
