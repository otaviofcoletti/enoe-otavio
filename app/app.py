from flask import Flask, render_template
import psycopg2
from datetime import datetime

app = Flask(__name__)

db_config = {
    'dbname': 'ultrassonic_sensor',
    'user': 'user',
    'password': 'password',
    'host': '172.19.0.2',
    'port': '5432'
}

def get_data():
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("SELECT * FROM ultrassonic ORDER BY epoch;")
    data = cur.fetchall()
    cur.close()
    conn.close()

    # Convert epoch to human-readable date and time
    converted_data = []
    for row in data:
        # Convert epoch to datetime
        date_time = datetime.fromtimestamp(int(row[0]))
        # Format the date and time as 'YYYY-MM-DD HH:MM:SS'
        formatted_date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
        # Append the formatted date_time with the measurement
        converted_data.append((formatted_date_time, row[1]))
    
    return converted_data

@app.route('/')
def index():
    data = get_data()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
