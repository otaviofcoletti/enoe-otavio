#!/bin/bash

# Encerrar todos os processos Python e Mosquitto
killall python3
sudo systemctl stop mosquitto

# Encerrar todas as sessões do screen
screen -ls | grep Detached | cut -d. -f1 | awk '{print $1}' | xargs -r kill

# Parar e remover os containers do Docker Compose
cd "/home/otavio/Área de Trabalho/enoe-otavio/Database"
docker compose down