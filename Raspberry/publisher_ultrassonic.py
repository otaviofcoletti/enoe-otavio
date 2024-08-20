import asyncio
import logging
import os
import json
import psutil
import csv
import datetime
from gmqtt import Client as MQTTClient
import serial

# Instâncias do ADC e serial
ser = serial.Serial('/dev/ttyAMA0', 9600)

# Configurações de logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Caminho para o arquivo de buffer
buffer_file = "message_buffer.json"

# Carregar configurações
with open("config.json") as f:
    config = json.load(f)

mqtt_config = config["MQTT"]
broker_endpoint = mqtt_config["broker_endpoint"]
port = mqtt_config["port"]
credentials_config = config["CREDENTIALS"]
username = credentials_config["username"]
password = credentials_config["password"]
interval_system_cfg = config["SYSTEM"]
interval_system_seconds = interval_system_cfg["interval_system_seconds"]

# MQTT Client Setup
client = MQTTClient("Raspberry PI") # !!!!!

# Função para carregar buffer de mensagens de um arquivo JSON
def load_buffer_from_file():
    if os.path.exists(buffer_file):
        with open(buffer_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logging.error("Erro ao carregar o arquivo de buffer JSON. Criando buffer vazio.")
                return []
    return []

# Função para salvar o buffer em um arquivo JSON
def save_buffer_to_file():
    with open(buffer_file, 'w') as f:
        json.dump(message_buffer, f)

# Carregar buffer de mensagens
message_buffer = load_buffer_from_file()

# Função chamada ao conectar-se ao broker
async def on_connect(client, flags, rc, properties):
    logging.info("Conectado ao broker MQTT.")
    await flush_buffered_messages()

# Função chamada ao desconectar-se
async def on_disconnect(client, packet, exc=None):
    logging.error("Desconectado do broker MQTT. Reconectando...")
    await asyncio.sleep(5)
    await client.connect(broker_endpoint, port)

# Publicar mensagens com buffer
async def publish_message(topic, payload):
    try:
        await client.publish(topic, json.dumps(payload))
        logging.info(f"Publicado: {topic} -> {payload}")
    except Exception as e:
        logging.error(f"Erro ao publicar mensagem: {e}. Salvando no buffer.")
        message_buffer.append((topic, payload))
        save_buffer_to_file()  # Salvar o buffer no arquivo após adicionar nova mensagem

# Reenviar mensagens do buffer
async def flush_buffered_messages(): # Aqui ele só apaga o buffer quando envia tudo
    global message_buffer
    for topic, payload in message_buffer:
        try:
            await client.publish(topic, json.dumps(payload))
            logging.info(f"Mensagem do buffer enviada: {topic} -> {payload}")
        except Exception as e:
            logging.error(f"Erro ao reenviar mensagem: {e}")
            return  # Sair se não conseguir reenviar para tentar depois
    message_buffer.clear()
    save_buffer_to_file()  # Limpar o buffer no arquivo JSON

# Funções para ler sensores
async def read_sensors():
    while True:
        try:
            cpu_usage = psutil.cpu_percent()
            cpu_temp = float(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1000.0
            ram_info = psutil.virtual_memory().percent
            storage_info = psutil.disk_usage('/').percent
            distance_value = ser.read(6).decode().replace("R", "").replace("\r", "")

            # Publicar leituras
            await publish_message("system/cpu_usage", {"value": cpu_usage})
            await publish_message("system/cpu_temp", {"value": cpu_temp})
            await publish_message("system/ram_usage", {"value": ram_info})
            await publish_message("system/storage_usage", {"value": storage_info})
            await publish_message("sensors/distance", {"value": distance_value})

            logging.info("Leituras publicadas com sucesso.")

        except Exception as e:
            logging.error(f"Erro ao ler sensores: {e}")

        await asyncio.sleep(interval_system_seconds)

# Inicialização do MQTT e loop principal
async def main():
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.set_auth_credentials(username, password)

    try:
        await client.connect(broker_endpoint, port)
    except Exception as e:
        logging.error(f"Erro ao conectar-se ao broker: {e}")
        return

    await asyncio.gather(read_sensors())

if __name__ == "__main__":
    asyncio.run(main())
