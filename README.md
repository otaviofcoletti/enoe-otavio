# enoe-otavio


## Week one

### Tests on mqtt and ultrassonic sensor

The publisher_ultrassonic.py publishes the data on a public broker for tests, then the mqtt_db.py subscribes the topic and writes on a Database

The database is a Postgres docker, the configurations are on Database folder

To run this follow the commands:

Clone the repository

```git clone git@github.com:otaviofcoletti/enoe-otavio.git```

Acess the folder MQTT_Broker, run

```
mosquitto -c config-server.conf -v
```

Now the broker is initialized



Run on raspberry

```publisher_ultrassonic.py```

On the pc acess the folder Database

```cd Database```

Run 

```docker compose up -d```
```cd ..```

Acess the folder Server, then run

```
mqtt_db_control.py
```

## Week Two

### Create a local mqtt broker

Acess the folder app and run

```
python3 app.py
```




Rede Wifi 

4G-UFI-552
Senha: Enoe2023

#!/bin/bash

# Nome da rede (SSID) e senha da rede Wi-Fi
SSID="nome_da_rede_wifi"
PASSWORD="senha_da_rede"

# Conectar à rede Wi-Fi
nmcli dev wifi connect "$SSID" password "$PASSWORD"

# Verificar se a conexão foi bem-sucedida
if [ $? -eq 0 ]; then
    echo "Conectado à rede Wi-Fi $SSID com sucesso!"
else
    echo "Falha ao conectar à rede Wi-Fi $SSID."
fi
