import psycopg2
import time
# docker exec -it postgres psql -U user -d ultrassonic_sensor

class SensorDataBuffer:
    def __init__(self, db_config, buffer_size=10, flush_interval=60):
        # Configurações de conexão com o banco de dados
        self.conn = psycopg2.connect(**db_config)
        self.cur = self.conn.cursor()

        # Buffer para armazenar os dados temporariamente
        self.buffer = []

        # Configurações do buffer
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval

        # Timer para controlar o envio periódico dos dados
        self.last_flush_time = time.time()

    def collect_data(self):
        # Simulação de coleta de dados
        return (int(time.time()), "distancia")

    def flush_buffer(self):
        if self.buffer:
            try:
                # Inserir os dados em lote no banco de dados
                insert_query = "INSERT INTO ultrassonic (epoch, distance) VALUES (%s, %s)"
                self.cur.executemany(insert_query, self.buffer)
                self.conn.commit()
                print(f"Enviado {len(self.buffer)} registros para o banco de dados.")
                self.buffer = []  # Limpar o buffer após envio
            except Exception as e:
                print(f"Erro ao enviar dados: {e}")
                self.conn.rollback()

    def run(self):
        x = 0
        while (x < 10):
            # Coletar os dados do sensor
            data = self.collect_data()

            # Adicionar dados ao buffer
            self.buffer.append(data)

            # Verificar se o buffer atingiu o tamanho definido
            if len(self.buffer) >= self.buffer_size:
                self.flush_buffer()

            # Verificar se o tempo definido para envio foi atingido
            if time.time() - self.last_flush_time >= self.flush_interval:
                self.flush_buffer()
                self.last_flush_time = time.time()

            # Pequena pausa (simulando a frequência de coleta de dados)
            time.sleep(1)

            x = x + 1

    def close(self):
        # Fechar a conexão ao final
        self.cur.close()
        self.conn.close()

# Exemplo de uso
if __name__ == "__main__":
    db_config = {
        'dbname': 'ultrassonic_sensor',
        'user': 'user',
        'password': 'password',
        'host': '172.19.0.2',
        'port': '5432'
    }

    buffer = SensorDataBuffer(db_config)
    
    try:
        buffer.run()
    except KeyboardInterrupt:
        buffer.close()