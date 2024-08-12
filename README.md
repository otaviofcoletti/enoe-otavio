# enoe-otavio


## Week one

### Tests on mqtt and ultrassonic sensor

The publisher_ultrassonic.py publishes the data on a public broker for tests, then the mqtt_db.py subscribes the topic and writes on a Database

The database is a Postgres docker, the configurations are on Database folder

To run this follow the commands:

Clone the repository

```git clone git@github.com:otaviofcoletti/enoe-otavio.git```

Run on raspberry

```publisher_ultrassonic.py```

On the pc acess the folder Database

```cd Database```

Run 

```docker compose -d```
```cd ..```

Then run 

```mqtt_db.py```

## Week Two

### Create a local mqtt broker
