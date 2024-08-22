#!/bin/bash

# Matar o script run_publisher.sh
pkill -f run_publisher.sh

# Matar todos os processos Python3
killall python3

# Mensagem de confirmação
echo "Terminated run_publisher.sh and all Python3 processes."
