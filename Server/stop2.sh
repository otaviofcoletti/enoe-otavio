#!/bin/bash

# Encerrar a sessão do Mosquitto
screen -S mosquitto_session -X stuff 'sudo systemctl stop mosquitto \n'
screen -S mosquitto_session -X quit
echo "Mosquitto session stopped."

# Encerrar a sessão do Docker (Database)
screen -S database_session -X stuff 'docker compose down \n'
screen -S database_session -X quit
echo "Database session stopped."

# Encerrar a sessão do Python subscriber
screen -S python_subscriber_session -X stuff 'killall python3 \n'
screen -S python_subscriber_session -X quit
echo "Python subscriber session stopped."

# Encerrar a sessão do Python app
screen -S python_app_session -X quit
echo "Python app session stopped."

echo "All screen sessions have been stopped."
