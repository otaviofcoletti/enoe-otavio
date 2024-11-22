from flask import Flask, render_template, request
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)

db_config = {
    'dbname': 'ultrassonic_sensor',
    'user': 'user',
    'password': 'password',
    'host': '172.18.0.2',
    'port': '5432'
}

def get_data(day, interval):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    # Convert 'epoch' to bigint before applying to_timestamp
    cur.execute("SELECT * FROM ultrassonic WHERE to_char(to_timestamp(epoch::bigint), 'YYYY-MM-DD') = %s ORDER BY epoch;", (day,))
    data = cur.fetchall()
    cur.close()
    conn.close()

    converted_data = []
    for row in data:
        date_time = datetime.fromtimestamp(int(row[0]))
        formatted_date_time = date_time.strftime('%Y-%m-%d %H-%M-%S')
        converted_data.append((formatted_date_time, row[1]))
    
    # Filtrar dados com base no intervalo
    filtered_data = []
    last_time = None
    for date_time, value in converted_data:
        if last_time is None or (datetime.strptime(date_time, '%Y-%m-%d %H-%M-%S') - last_time).total_seconds() >= interval * 60:
            filtered_data.append((date_time, value))
            last_time = datetime.strptime(date_time, '%Y-%m-%d %H-%M-%S')
    
    return filtered_data

@app.route('/', methods=['GET', 'POST'])
def index():
    day = request.form.get('day', datetime.now().strftime('%Y-%m-%d'))
    interval = int(request.form.get('interval', 1))
    data = get_data(day, interval)
    
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    
    return render_template('index.html', data=data, day=day, labels=labels, values=values)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
