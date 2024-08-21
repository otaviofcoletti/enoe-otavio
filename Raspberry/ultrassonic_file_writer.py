import serial
import time
import csv
import datetime
import socket
import json
import os

# Carregar as configurações do arquivo config.json
with open("config.json") as f:
    config = json.load(f)

# Frequência de geração de arquivos em minutos (pode ser alterado conforme necessário)
csv_interval_minutes = config.get("CSV_INTERVAL_MINUTES", 2)
csv_interval_seconds = csv_interval_minutes * 60

def set_serial():
    ser = serial.Serial('/dev/ttyAMA0', 9600)
    return ser

def get_line(ser=None):
    line = int(ser.read(6).decode().replace("R", "").replace("\r", ""))
    return line

def main():
    ser = set_serial()
    
    # Criar a pasta "data" se não existir
    if not os.path.exists("data"):
        os.makedirs("data")
    
    while True:
        # Nome do arquivo CSV baseado na data e hora atual
        timestamp = datetime.datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
        filename = os.path.join("data", f"readings_{date_str}.csv")
        
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "hostname", "distance", "epoch"])  # Header

            end_time = time.time() + csv_interval_seconds
            while time.time() < end_time:
                time.sleep(1)
                ser.reset_input_buffer()
                distance = get_line(ser)
                message = [
                    datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                    socket.gethostname(),
                    distance,
                    int(time.time())
                ]
                writer.writerow(message)

if __name__ == "__main__":
    main()
