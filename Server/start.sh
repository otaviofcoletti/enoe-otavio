#!/bin/bash

# Start the first screen session with Mosquitto in /home/enoe/server

screen -dmS mosquitto_session
screen -S mosquitto_session -X stuff 'cd /home/enoe/server\n'
screen -S mosquitto_session -X stuff 'mosquitto -c config-server.conf -v\n'

# Start the second screen session with the Python publisher in /home/enoe/server/publisher
screen -dmS python_publisher_session
screen -S python_publisher_session -X stuff 'cd /home/enoe/server/publisher\n'
screen -S python_publisher_session -X stuff 'python3 publisher.py\n'

# Start the third screen session with the Python app in /media/storage/backup/ImageVisualizer
screen -dmS python_app_session
screen -S python_app_session -X stuff 'cd /media/storage/backup/ImageVisualizer\n'
screen -S python_app_session -X stuff 'python3 app.py\n'

echo "Screen sessions started:"
echo "- Mosquitto session: mosquitto_session"
echo "- Python publisher session: python_publisher_session"
echo "- Python app session: python_app_session"