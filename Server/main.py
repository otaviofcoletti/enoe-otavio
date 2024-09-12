import json
import os
import time
import base64
from datetime import datetime
from MQTTHandlerSubscriber import MQTTHandlerSubscriber
from DatabaseHandler import DatabaseHandler

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
    topics = ["ultrassonic", "image"]

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

    while True:
        if not mqtt_handler.queue.empty():
            message_data = mqtt_handler.queue.get()
            topic = message_data['topic']
            message = message_data['message']
            print(f"Processing message from topic {topic}")

            if topic == 'ultrassonic':
                # Assuming the message is a JSON with fields 'epoch' and 'distance'
                try:
                    json_data = json.loads(message)
                    timestamp, hostname, distance, epoch = json_data

                    db_handler.insert_data('ultrassonic',epoch, distance)
                except Exception as e:
                    print(f"Error processing message: {e}")

            elif topic == 'image':
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

                    # Save the image to a file
                    file_path = os.path.join(day_path, filename)
                    print(f"Saving image to {file_path}")
                    with open(file_path, 'wb') as file:
                        file.write(image_data)
                        file.flush()
                        os.fsync(file.fileno())  # Garante que o sistema operacional grave os dados no disco

                    db_handler.insert_data('images',filename, day_path)

                except Exception as e:
                    print(f"Error processing message: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
