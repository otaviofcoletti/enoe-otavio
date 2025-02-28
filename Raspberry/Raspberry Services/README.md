# enoe-otavio


## Serviços

### Aqui estão os arquivos de serviços, são todos os terminados em .service, abaixo instruções de como você deve proceder em cada caso:


#### Primeira configuração do sistema


#### Sistema já configurado, instruções de como rodar os serviços
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

## Instalar open cv globalmente, ele não funciona baixando pelo pip

## sudo apt install python3-opencv

## O criador de imagem deve ter o caminho global do python,  resto mantem no ambiente.