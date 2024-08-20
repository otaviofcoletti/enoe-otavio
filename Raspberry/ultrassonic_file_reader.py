import paho.mqtt.client as mqtt
import json
import os
import time
import glob

# Carregar as configurações do arquivo config.json
with open("config.json") as f:
    config = json.load(f)

mqtt_config = config["MQTT"]
broker_endpoint = mqtt_config["broker_endpoint"]
port = mqtt_config["port"]

credentials_config = config["CREDENTIALS"]
username = credentials_config["username"]
password = credentials_config["password"]

def on_publish(client, userdata, mid, reason_code, properties=None):
    try:
        userdata.remove(mid)
    except KeyError:
        print("Could not publish")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to broker")
        client.connected_flag = True
    else:
        print(f"Failed to connect, return code {rc}")
        client.connected_flag = False

def set_client(server, port, username, password):
    unacked_publish = set()
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_publish = on_publish
    mqttc.on_connect = on_connect
    mqttc.user_data_set(unacked_publish)
    mqttc.username_pw_set(username, password)  # Configurar credenciais
    mqttc.connected_flag = False
    mqttc.connect(server, port=port)
    mqttc.loop_start()
    return mqttc, unacked_publish

def publish_file(filename, mqttc, unacked_publish):
    with open(filename, mode='r') as file:
        lines = file.readlines()
        for line in lines[1:]:  # Skip header
            json_data = json.dumps(line.strip().split(','))
            msg_info = mqttc.publish("paho/test/topic", json_data, qos=0)
            unacked_publish.add(msg_info.mid)
            if len(unacked_publish):
                time.sleep(0.1)
            msg_info.wait_for_publish()

    # Apagar o arquivo após envio
    os.remove(filename)

def main():
    mqttc, unacked_publish = set_client(server=broker_endpoint, port=port, username=username, password=password)
    
    # Esperar pela conexão
    while not mqttc.connected_flag:
        print("Waiting for connection...")
        time.sleep(1)
    
    while True:
        # Encontrar arquivos CSV para processar
        for filename in glob.glob("readings_*.csv"):
            publish_file(filename, mqttc, unacked_publish)
        time.sleep(60)  # Esperar antes de verificar novos arquivos

if __name__ == "__main__":
    main()
