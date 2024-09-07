import serial
import paho.mqtt.client as mqtt
import time
import socket
import datetime
import json

def set_serial():
    """Initialize and return the serial port."""
    return serial.Serial('/dev/ttyAMA0', 9600)

def on_publish(client, userdata, mid, reason_code, properties):
    """Callback for when a message is published."""
    try:
        userdata.remove(mid)
    except KeyError:
        print("Failed to remove mid from unacked_publish set.")

def set_client(server=None):
    """Initialize and return the MQTT client and unacked_publish set."""
    unacked_publish = set()
    mqttc = mqtt.Client()  # Use default constructor
    mqttc.on_publish = on_publish
    mqttc.user_data_set(unacked_publish)
    mqttc.connect(server)
    mqttc.loop_start()
    return mqttc, unacked_publish

def get_line(ser=None):
    """Read and parse a line from the serial port."""
    line = ser.read(6).decode().strip().replace("R", "")
    return int(line)

def send_line(line=None, mqttc=None, unacked_publish=None):
    """Publish a line of data to the MQTT topic."""
    json_data = json.dumps(line)
    msg_info = mqttc.publish("paho/test/topic", json_data, qos=0)
    unacked_publish.add(msg_info.mid)
    
    # Wait for the message to be acknowledged
    if len(unacked_publish):
        time.sleep(0.1)
    msg_info.wait_for_publish()

def main():
    """Main function to run the script."""
    ser = set_serial()
    mqttc, unacked_publish = set_client(server="mqtt.eclipseprojects.io")
    
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

if __name__ == "__main__":
    main()
