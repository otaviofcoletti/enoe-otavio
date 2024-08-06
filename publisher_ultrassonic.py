import serial
import paho.mqtt.client as mqtt
import time 
import socket
import datetime 

def set_serial():
	ser = serial.Serial('/dev/ttyAMA0', 9600)
	return ser

def on_publish(client, userdata, mid, reason_code, properties):
    try:
        userdata.remove(mid)
    except KeyError:
        print("Could not publish")
  

def set_client(server = None):
	unacked_publish = set()
	mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
	mqttc.on_publish = on_publish
	mqttc.user_data_set(unacked_publish)
	mqttc.connect(server)
	mqttc.loop_start()
	return mqttc, unacked_publish
        

def get_line(ser = None):
	line = int(ser.read(6).decode().replace("R", "").replace("\r", ""))
	return line

def send_line(line = None, mqttc = None, unacked_publish = None):
	msg_info = mqttc.publish("paho/test/topic", line, qos=0)
	unacked_publish.add(msg_info.mid)
	if len(unacked_publish):
		time.sleep(0.1)
	msg_info.wait_for_publish()

def main():
	ser = set_serial()
	mqttc, unacked_publish = set_client(server = "mqtt.eclipseprojects.io")
	while True:
		time.sleep(1)
		ser.reset_input_buffer()
		line = get_line(ser)
		message = f"{datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')},{socket.gethostname()},{line}"
		send_line(line = message, mqttc = mqttc, unacked_publish = unacked_publish)
		

main()
