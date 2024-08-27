#!/bin/bash

# Start the first screen session with Mosquitto in /home/enoe/server

screen -dmS mosquitto_session
screen -S mosquitto_session -X stuff 'cd "/home/otavio/Área de Trabalho/enoe-otavio/MQTT_Broker"\n'
screen -S mosquitto_session -X stuff 'mosquitto -c config-server.conf -v\n'

# Start the second screen session with the Python publisher in /home/enoe/server/publisher
screen -dmS database_session
screen -S database_session -X stuff 'cd "/home/otavio/Área de Trabalho/enoe-otavio/Database"\n'
screen -S database_session -X stuff 'docker compose up -d\n'

screen -dmS python_subscriber_session
screen -S python_subscriber_session -X stuff 'cd "/home/otavio/Área de Trabalho/enoe-otavio/Server"\n'
screen -S python_subscriber_session -X stuff 'python3 mqtt_db_control.py\n'

# Start the third screen session with the Python app in /media/storage/backup/ImageVisualizer
screen -dmS python_app_session
screen -S python_app_session -X stuff 'cd "/home/otavio/Área de Trabalho/enoe-otavio/app"\n'
screen -S python_app_session -X stuff 'python3 app.py\n'

echo "Screen sessions started:"
echo "- Mosquitto session: mosquitto_session"
echo "- Python subscriber session: python_subscriber_session"
echo "- database session: database_session"
echo "- Python app session: python_app_session"
