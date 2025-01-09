from flask import Flask, render_template, request
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)

db_config = {
    'dbname': 'enoe_database',
    'user': 'user',
    'password': 'password',
    'host': '172.18.0.2',
    'port': '5432'
}

def get_data(day, interval):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    # Ajustando o timestamp para GMT-3 no SQL
    cur.execute("""
        SELECT to_char(to_timestamp(epoch::bigint) AT TIME ZONE 'America/Sao_Paulo', 'YYYY-MM-DD HH24:MI:SS') AS timestamp_local,
               distance_mm
        FROM ultrasonic
        WHERE to_char(to_timestamp(epoch::bigint) AT TIME ZONE 'America/Sao_Paulo', 'YYYY-MM-DD') = %s
        ORDER BY epoch;
    """, (day,))
    data = cur.fetchall()
    cur.close()
    conn.close()

    # Filtrar dados com base no intervalo em minutos
    filtered_data = []
    last_time = None
    for timestamp_local, value in data:
        current_time = datetime.strptime(timestamp_local, '%Y-%m-%d %H:%M:%S')
        if last_time is None or (current_time - last_time).total_seconds() >= interval * 60:
            filtered_data.append((timestamp_local, value))
            last_time = current_time

    return filtered_data

@app.route('/', methods=['GET', 'POST'])
def index():
    # Obtém o dia atual no horário de São Paulo
    day = request.form.get('day', (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d'))
    interval = int(request.form.get('interval', 1))
    data = get_data(day, interval)
    
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    
    return render_template('index.html', data=data, day=day, labels=labels, values=values)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
