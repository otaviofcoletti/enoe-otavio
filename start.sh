#!/bin/bash

# Obter o diretório base do projeto (o diretório atual onde o script está sendo executado)
BASE_DIR=$(pwd)

# Start the first screen session with Mosquitto in ./MQTT_Broker
screen -dmS mosquitto_session
screen -S mosquitto_session -X stuff "cd \"$BASE_DIR/MQTT_Broker\"\n"
screen -S mosquitto_session -X stuff 'mosquitto -c config-server.conf -v\n'

# Start the third screen session with the Python subscriber in ./Server
screen -dmS python_subscriber_session
screen -S python_subscriber_session -X stuff "cd \"$BASE_DIR/Server\"\n"
screen -S python_subscriber_session -X stuff 'python3 main.py\n'

# Start the fourth screen session with the Python app in ./app
screen -dmS python_app_session
screen -S python_app_session -X stuff "cd \"$BASE_DIR/app\"\n"
screen -S python_app_session -X stuff 'python3 app.py\n'

echo "Screen sessions started:"
echo "- Mosquitto session: mosquitto_session"
echo "- Python subscriber session: python_subscriber_session"
echo "- Python app session: python_app_session"
