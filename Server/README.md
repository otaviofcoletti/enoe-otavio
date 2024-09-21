# Projeto de Monitoramento com MQTT e Banco de Dados

Este projeto é um sistema de monitoramento que utiliza MQTT para comunicação entre dispositivos e um banco de dados PostgreSQL para armazenamento de dados. O sistema é composto por um cliente MQTT que se inscreve em tópicos específicos e armazena as mensagens recebidas no banco de dados. Além disso, o sistema também processa e armazena imagens recebidas via MQTT.

## Estrutura do Projeto

- `main.py`: Script principal que inicializa e gerencia o cliente MQTT e o manipulador de banco de dados.
- `MQTTHandlerSubscriber.py`: Classe que gerencia a conexão e a comunicação com o broker MQTT.
- `DatabaseHandler.py`: Classe que gerencia a conexão e as operações com o banco de dados PostgreSQL.
- `config.json`: Arquivo de configuração contendo as informações do broker MQTT, credenciais e configurações do banco de dados.
- `logs/`: Diretório onde os logs do sistema são armazenados.

## Pré-requisitos

- Python 3.6 ou superior
- PostgreSQL
- Broker MQTT (por exemplo, Mosquitto)

## Instalação

### 1. Clone o repositório

```bash
git clone git@github.com:otaviofcoletti/enoe-otavio.git
cd enoe-otavio

python3 -m venv server_venv
source server_venv/bin/activate

pip install -r requirements.txt
```