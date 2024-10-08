import pandas as pd
from flask import Flask, render_template, request
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Load CSVs
sensor_data = pd.read_csv('/home/intermidia/enoe-otavio/Server/ultrassonic_log_delays.csv')
image_data = pd.read_csv('/home/intermidia/enoe-otavio/Server/image_log_delays.csv')

@app.route("/", methods=['GET', 'POST'])
def index():
    # Default values
    data_type = 'sensor'
    y_axis = 'log_epoch_difference'
    start_date = sensor_data['log_time'].min()
    end_date = sensor_data['log_time'].max()

    # Handle form submission
    if request.method == 'POST':
        data_type = request.form.get('data_type')
        y_axis = request.form.get('y_axis')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

    # Choose the correct dataset
    data = sensor_data if data_type == 'sensor' else image_data

    # Filter data by date range
    filtered_data = data[(data['log_time'] >= start_date) & (data['log_time'] <= end_date)]

    # Plotly figure
    fig = px.line(filtered_data, x='log_time', y=y_axis, title=f"{data_type.capitalize()} Log Delays")
    graph_html = pio.to_html(fig, full_html=False)

    return render_template('index.html', graph_html=graph_html, y_axis=y_axis, start_date=start_date, end_date=end_date)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
