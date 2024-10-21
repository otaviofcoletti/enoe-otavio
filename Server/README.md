# Projeto de Monitoramento com MQTT e Banco de Dados

Este projeto é um sistema de monitoramento que utiliza MQTT para comunicação entre dispositivos e um banco de dados PostgreSQL para armazenamento de dados. O sistema é composto por um cliente MQTT que se inscreve em tópicos específicos e armazena as mensagens recebidas no banco de dados. Além disso, o sistema também processa e armazena imagens recebidas via MQTT.

## Estrutura do Projeto

- `main.py`: Script principal que inicializa e gerencia o cliente MQTT e o manipulador de banco de dados.
- `MQTTHandlerSubscriber.py`: Classe que gerencia a conexão e a comunicação com o broker MQTT.
- `DatabaseHandler.py`: Classe que gerencia a conexão e as operações com o banco de dados PostgreSQL.
- `config.json`: Arquivo de configuração contendo as informações do broker MQTT, credenciais e configurações do banco de dados.
- `main_subscriber.service`: Arquivo de configuração do serviço que mantém a main.py funcionando.
- `images/`: Diretório onde as imagens são salvas
- `logs/`: Diretório onde os logs do sistema são armazenados.
- `Testes/: Pasta onde ficam registrados códigos de teste.

## Pré-requisitos

- Python 3.6 ou superior
- PostgreSQL
- Broker MQTT (por exemplo, Mosquitto)

## Instalação

### 1. Clone o repositório

```bash
git clone git@github.com:otaviofcoletti/enoe-otavio.git
cd enoe-otavio
```

### 2. Instale as dependências
```bash

python3 -m venv server_venv
source server_venv/bin/activate

# Pode utilizar apenas o comando abaixo, mas recomendo utilizar o ambiente virtual

pip install -r requirements.txt
```

### 3. Edite o config.json para o endereço IP, portas, credenciais e etc

```bash
{
  "MQTT": {
    "broker_endpoint": "localhost",
    "port": 1883
  },
  "CREDENTIALS": {
    "username": "server",
    "password": "server.publisher"
  },
  "DATABASE": {
    "dbname": "ultrassonic_sensor",
    "user": "user",
    "password": "password",
    "host": "172.18.0.2",
    "port": "5432"
  }
}
```

### 4. Atualize o arquivo main_subscriber.service
```bash
[Unit]
Description=Main Subscriber Service
After=network.target

[Service]
Type=simple
User=intermidia
Group=intermidia
WorkingDirectory=/home/intermidia/enoe-otavio/Server
Environment="PATH=/home/intermidia/enoe-otavio/enoe/bin"
ExecStart=/home/intermidia/enoe-otavio/enoe/bin/python3 /home/intermidia/enoe-otavio/Server/main.py
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=inherit

[Install]
WantedBy=multi-user.target
```

Copie o caminho absoluto dos arquivos e diretórios que são necessários e atualize o arquivo.

### 5. Copie para a pasta de serviços e ative o serviço

```bash
sudo cp main_subscriber.service /etc/systemd/system/
```

#### Ativar o serviço para iniciar no boot
```bash
sudo systemctl enable main_subscriber.service
```

#### Recarregar as configurações do systemd (após modificar arquivos de serviço)
```
sudo systemctl daemon-reload

Este projeto é um sistema de monitoramento que utiliza MQTT para comunicação entre dispositivos e um banco de dados PostgreSQL para armazenamento de dados. O sistema é composto por um cliente MQTT que se inscreve em tópicos específicos e armazena as mensagens recebidas no banco de dados. Além disso, o sistema também processa e armazena imagens recebidas via MQTT.

## Estrutura do Projeto

- `main.py`: Script principal que inicializa e gerencia o cliente MQTT e o manipulador de banco de dados.
- `MQTTHandlerSubscriber.py`: Classe que gerencia a conexão e a comunicação com o broker MQTT.
- `DatabaseHandler.py`: Classe que gerencia a conexão e as operações com o banco de dados PostgreSQL.
- `config.json`: Arquivo de configuração contendo as informações do broker MQTT, credenciais e configurações do banco de dados.
- `main_subscriber.service`: Arquivo de configuração do serviço que mantém a main.py funcionando.
- `images/`: Diretório onde as imagens são salvas
- `logs/`: Diretório onde os logs do sistema são armazenados.
- `Testes/`: Pasta onde ficam registrados códigos de teste.

## Pré-requisitos

- Python 3.6 ou superior
- PostgreSQL
- Broker MQTT (por exemplo, Mosquitto)

## Instalação

### 1. Clone o repositório

```bash
git clone git@github.com:otaviofcoletti/enoe-otavio.git
cd enoe-otavio
```

### 2. Instale as dependências
```bash

python3 -m venv server_venv
source server_venv/bin/activate
```

# Pode utilizar apenas o comando abaixo, mas recomendo utilizar o ambiente virtual
```bash
pip install -r requirements.txt
```

### 3. Edite o config.json para o endereço IP, portas, credenciais e etc

```bash
{
  "MQTT": {
    "broker_endpoint": "localhost",
    "port": 1883
  },
  "CREDENTIALS": {
    "username": "server",
    "password": "server.publisher"
  },
  "DATABASE": {
    "dbname": "ultrassonic_sensor",
    "user": "user",
    "password": "password",
    "host": "172.18.0.2",
    "port": "5432"
  }
}
```

### 4. Atualize o arquivo main_subscriber.service
```bash
[Unit]
Description=Main Subscriber Service
After=network.target

[Service]
Type=simple
User=intermidia
Group=intermidia
WorkingDirectory=/home/intermidia/enoe-otavio/Server
Environment="PATH=/home/intermidia/enoe-otavio/enoe/bin"
ExecStart=/home/intermidia/enoe-otavio/enoe/bin/python3 /home/intermidia/enoe-otavio/Server/main.py
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=inherit

[Install]
WantedBy=multi-user.target
```

Copie o caminho absoluto dos arquivos e diretórios que são necessários e atualize o arquivo.

### 5. Copie para a pasta de serviços e ative o serviço

```bash
sudo cp main_subscriber.service /etc/systemd/system/
```

#### Ativar o serviço para iniciar no boot
```bash
sudo systemctl enable main_subscriber.service
```

#### Recarregar as configurações do systemd (após modificar arquivos de serviço)
```bash
sudo systemctl daemon-reload
```

#### Iniciar o serviço
```bash
sudo systemctl start main_subscriber.service
```

#### Iniciar o serviço
```
sudo systemctl start main_subscriber.service
```

### Essas instruções devem fazer os códigos relacionados ao servidor funcionar, abaixo alguns comandos relacionados aos serviços que podem ser úteis

## Comandos do Systemd

### Iniciar o serviço
```bash
sudo systemctl start main_subscriber.service
```

### Parar o serviço
```bash
sudo systemctl stop main_subscriber.service
```

### Reiniciar o serviço
```bash
sudo systemctl restart main_subscriber.service
```

### Recarregar a configuração do serviço sem interrompê-lo
```bash
sudo systemctl reload main_subscriber.service
```

### Ativar o serviço para iniciar no boot
```bash
sudo systemctl enable main_subscriber.service
```

### Desativar o serviço para não iniciar no boot
```bash
sudo systemctl disable main_subscriber.service
```

### Verificar o status do serviço
```bash
systemctl status main_subscriber.service
```

### Ver os logs do serviço
```bash
journalctl -u main_subscriber.service
```

### Recarregar as configurações do systemd (após modificar arquivos de serviço)
```bash
sudo systemctl daemon-reload
```

## Como restaurar backup
https://www.youtube.com/watch?v=57FW16QvFJ8&ab_channel=CodeTotal


# Comandos

Ir na pasta Database/backups

Decompactar o arquivo usando gunzip

gunzip backup_20241008.sql.gz

Copie o arquivo para o container

docker cp backup_20241008.sql postgres:/backup.sql

Entrar no container 

docker exec -it postgres bash

Criar o novo banco:

createdb -U user ultrassonic_restored

Restaurar a partir do arquivo copiado

psql -U postgres -d ultrassonic_restored < backup.sql

Verificar se está tudo certo 

Entre agora no banco de dados, lembre-se que antes você estava apenas no container

psql -U user -d ultrassonic_restored

\dt para visualizar as tabelas

Lembrar de colocar o comando para o banco de dados voltar quando o pc reiniciar

Colocar como serviço os apps e o backup



Para configurar o docker iniciar após um reboot

https://stackoverflow.com/questions/49999068/docker-container-doesnt-start-after-reboot-with-enabling-systemd-script

Rode docker inspect -f "{{ .HostConfig.RestartPolicy.Name }}" <container name>

se aparecer "no"

Rode docker update --restart=always <container>

Rode novamente 
docker inspect -f "{{ .HostConfig.RestartPolicy.Name }}" <container name>

e deverá aparecer "always" no terminal


Ativar exporter para monitorar mqtt

https://github.com/hikhvar/mqtt2prometheus