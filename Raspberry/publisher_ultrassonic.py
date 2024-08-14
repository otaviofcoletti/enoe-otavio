import serial
import paho.mqtt.client as mqtt
import time
import socket
import datetime
import json

# Carregar as configurações do arquivo config.json
with open("config.json") as f:
    config = json.load(f)

mqtt_config = config["MQTT"]
broker_endpoint = mqtt_config["broker_endpoint"]
port = mqtt_config["port"]

credentials_config = config["CREDENTIALS"]
username = credentials_config["username"]
password = credentials_config["password"]

def set_serial():
    ser = serial.Serial('/dev/ttyAMA0', 9600)
    return ser

def on_publish(client, userdata, mid, reason_code, properties):
    try:
        userdata.remove(mid)
    except KeyError:
        print("Could not publish")

def on_connect(client, userdata, flags, rc):
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

def get_line(ser=None):
    line = int(ser.read(6).decode().replace("R", "").replace("\r", ""))
    return line

def send_line(line=None, mqttc=None, unacked_publish=None):
    if mqttc.connected_flag:
        json_data = json.dumps(line)
        msg_info = mqttc.publish("paho/test/topic", json_data, qos=0)
        unacked_publish.add(msg_info.mid)
        if len(unacked_publish):
            time.sleep(0.1)
        msg_info.wait_for_publish()
    else:
        print("Client is not connected, skipping publish")

def main():
    ser = set_serial()
    mqttc, unacked_publish = set_client(server=broker_endpoint, port=port, username=username, password=password)

    # Esperar pela conexão
    while not mqttc.connected_flag:
        print("Waiting for connection...")
        time.sleep(1)

    while True:
        time.sleep(1)
        ser.reset_input_buffer()
        distance = get_line(ser)
        message = {
            "timestamp": datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
            "hostname": socket.gethostname(),
            "distance": distance,
            "epoch": int(time.time())
        }
        send_line(line=message, mqttc=mqttc, unacked_publish=unacked_publish)

main()
