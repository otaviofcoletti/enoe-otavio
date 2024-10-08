import time
import pandas as pd
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import timezone
from datetime import timedelta

# Define paths for logs and output CSV files
log_file_path = 'log/DatabaseHandler.log'
sensor_csv_path = 'ultrassonic_log_delays.csv'
image_csv_path = 'image_log_delays.csv'

# Define log monitoring event handler
class LogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == log_file_path:
            with open(log_file_path, 'r') as f:
                logs = f.readlines()
            process_logs(logs)

def process_logs(logs):
    sensor_logs = []
    image_logs = []

    for log in logs:
        if "Data inserted successfully" in log:
            sensor_logs.append(log)
        elif "Image inserted successfully" in log:
            image_logs.append(log)

    sensor_data = []
    for log in sensor_logs:
        parts = log.split(' - ')
        log_time = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S,%f").replace(tzinfo=timezone.utc)
        epoch = int(parts[-1].split('=')[1].split(',')[0])
        sensor_data.append({
            "log_time": log_time,
            "epoch": epoch,
            "distance_cm": int(parts[-1].split('=')[2]),
            "log_epoch_difference": (log_time - datetime.fromtimestamp(epoch, tz=timezone.utc)).total_seconds()
        })

    image_data = []
    for log in image_logs:
        parts = log.split(' - ')
        log_time = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S,%f")
        image_epoch_str = parts[-1].split('=')[1].split('.')[0]
        image_time = datetime.strptime(image_epoch_str, "%d-%m-%Y_%H:%M:%S") + timedelta(hours=3)
        image_data.append({
            "log_time": log_time,
            "image_time": image_time,
            "log_epoch_difference": (log_time - image_time).total_seconds()
        })

    # Append data to CSVs
    append_to_csv(sensor_data, sensor_csv_path)
    append_to_csv(image_data, image_csv_path)

def append_to_csv(data, file_path):
    df = pd.DataFrame(data)
    df.to_csv(file_path, mode='a', header=not pd.io.common.file_exists(file_path), index=False)

if __name__ == "__main__":
    # Create observer for monitoring the log file
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path=log_file_path, recursive=False)

    # Start monitoring
    observer.start()
    print(f"Monitoring {log_file_path}...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
