from flask import Flask, render_template, request
import psycopg2
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

db_config = {
    'dbname': 'ultrassonic_sensor',
    'user': 'user',
    'password': 'password',
    'host': '172.18.0.2',
    'port': '5432'
}

def get_data(day):
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
        formatted_date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
        converted_data.append((formatted_date_time, row[1]))
    
    return converted_data


@app.route('/', methods=['GET', 'POST'])
def index():
    day = request.form.get('day', datetime.now().strftime('%Y-%m-%d'))
    view_type = request.form.get('view_type', 'table')  # 'table' or 'chart'
    tick_frequency = int(request.form.get('tick_frequency', 60))  # Frequency of x-axis ticks

    data = get_data(day)
    
    if view_type == 'chart':
        # Create a chart
        times = [row[0] for row in data]
        measurements = [row[1] for row in data]
        max_measurement = max(measurements)

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(times, measurements, color='blue')
        plt.axhline(y=max_measurement, color='red', linestyle='--', label=f'Máxima do dia: {max_measurement}')
        plt.xlabel('Tempo')
        plt.ylabel('Medição')
        plt.xticks(rotation=45, ha='right')
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(len(times) // tick_frequency))
        plt.tight_layout()
        
        # Save to a bytes buffer
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')

        return render_template('index.html', plot_url=plot_url, day=day, view_type=view_type, tick_frequency=tick_frequency)
    
    return render_template('index.html', data=data, day=day, view_type=view_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
