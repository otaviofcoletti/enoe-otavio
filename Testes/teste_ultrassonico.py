import serial
import paho.mqtt.client as mqtt
import time
import socket
import datetime
import json

def set_serial():
    """Initialize and return the serial port."""
    return serial.Serial('/dev/ttyS0', 9600)


def get_line(ser=None):
    """Read and parse a line from the serial port."""
    line = ser.read(6).decode().strip().replace("R", "")
    return int(line)



def main():
    """Main function to run the script."""
    ser = set_serial()
    
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
        print(message)

if __name__ == "__main__":
    main()

