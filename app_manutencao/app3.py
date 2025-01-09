from flask import Flask, jsonify, render_template
import psycopg2
from datetime import datetime

app = Flask(__name__)

db_config = {
    'dbname': 'enoe_database',
    'user': 'user',
    'password': 'password',
    'host': '172.18.0.2',
    'port': '5432'
}

def get_latest_data():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute("SELECT epoch, distance_mm FROM ultrasonic ORDER BY epoch DESC LIMIT 50;")
        data = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return []

    converted_data = []
    #print(f"DATA: {data}")
    for row in data:
        try:
            date_time = datetime.fromtimestamp(int(row[0])).isoformat()
            converted_data.append((date_time, row[1]))
        except Exception as e:
            print(f"Erro ao converter dados: {e}")
    
    # Ordenar os dados em ordem cronológica
    converted_data.sort(key=lambda x: x[0])

    return converted_data

@app.route('/', methods=['GET'])
def index():
    return render_template('index3.html')

@app.route('/data', methods=['GET'])
def data():
    latest_data = get_latest_data()
    labels = [row[0] for row in latest_data]
    values = [row[1] for row in latest_data]
    return jsonify({'labels': labels, 'values': values})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)
