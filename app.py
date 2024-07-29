import datetime
import serial
import threading
import time
import mysql.connector
from flask import Flask, render_template, jsonify, request
import requests
import serial.tools.list_ports
from queue import Queue

app = Flask(__name__)
ser = None
data_queue = Queue()

db_config = {
    'user': 'root',
    'password': '',
    'host': '****',
    'database': '****',
    'port': ***
}

raspberry_pi_url = "http://**********/receive-data"

last_reading = {"value": 0.00, "time": "", "status": ""}
last_reading_lock = threading.Lock()
last_update_time = datetime.datetime.now()

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def open_serial_port():
    global ser
    available_ports = list_serial_ports()
    print(f"Available ports: {available_ports}")
    while ser is None:
        try:
            port = 'COM18' if 'COM18' in available_ports else (available_ports[0] if available_ports else None)
            if port is None:
                print("No available serial ports found. Retrying in 5 seconds...")
                time.sleep(5)
                continue
            ser = serial.Serial(port, 2400, timeout=1)
            print(f"Serial port {port} opened successfully.")
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
            ser = None
            time.sleep(5)
        except PermissionError as e:
            print(f"Permission denied while opening serial port: {e}")
            time.sleep(5)

def read_sensor():
    global last_reading
    global ser
    global last_update_time
    open_serial_port()

    while True:
        try:
            if ser and ser.readable():
                line = ser.readline().decode('utf-8').strip()
                if line:
                    try:
                        parts = line.split('.')
                        if len(parts) < 2:
                            print("Invalid data received from sensor")
                            continue

                        integer_part = parts[0].lstrip('0') or '0'
                        decimal_part = parts[1][:2]
                        value = float(f"{integer_part}.{decimal_part}")
                        value = round(value, 2)
                    except ValueError:
                        print("Invalid data received from sensor")
                        continue

                    now = datetime.datetime.now()
                    if value < 8.0:
                        status = "AMAN"
                    elif 8.0 <= value <= 10.0:
                        status = "ALERT"
                    else:
                        status = "BAHAYA"
                        
                    current_time = now.strftime('%Y-%m-%d %H:%M:%S')

                    with last_reading_lock:
                        last_reading = {"value": format(value, '.2f'), "time": current_time, "status": status}
                        last_update_time = now

                    data_line = f"Sensor Value: {format(value, '.2f')} µSv/jam\nCurrent Time: {current_time}\nStatus: {status}\n"
                    print(data_line)

                    data_queue.put((value, current_time, status))

                time.sleep(1)
            else:
                open_serial_port()
        except serial.SerialException as e:
            print(f"Serial port error: {e}")
            ser = None
            open_serial_port()
            time.sleep(5)
        except Exception as e:
            print(f"Error in read_sensor thread: {e}")
            time.sleep(5)

def store_data():
    last_db_time = time.time()
    last_raspberry_time = time.time()

    while True:
        try:
            value, current_time, status = data_queue.get()
            current_time_epoch = time.time()

            if current_time_epoch - last_db_time >= 5:
                try:
                    db_connection = mysql.connector.connect(**db_config)
                    cursor = db_connection.cursor()
                    query = "INSERT INTO readings (sensor_value, reading_time, status) VALUES (%s, %s, %s)"
                    cursor.execute(query, (value, current_time, status))
                    db_connection.commit()
                    cursor.close()
                    db_connection.close()
                    print("Data stored in DB")
                    last_db_time = current_time_epoch
                except mysql.connector.Error as err:
                    print(f"Error: {err}")

            if current_time_epoch - last_raspberry_time >= 5:
                send_data_to_raspberry(value, current_time, status)
                last_raspberry_time = current_time_epoch
        except Exception as e:
            print(f"Error in store_data thread: {e}")
            time.sleep(5)

def send_data_to_raspberry(value, current_time, status):
    try:
        data = {"value": value, "time": current_time, "status": status}
        print(f"Sending data to Raspberry Pi: {data}")
        response = requests.post(raspberry_pi_url, json=data)
        if response.status_code == 200:
            print("Data successfully sent to Raspberry Pi")
        else:
            print(f"Failed to send data to Raspberry Pi: {response.status_code}")
    except Exception as e:
        print(f"Error sending data to Raspberry Pi: {e}")

@app.route('/')
def index():
    print("Rendering index.html")
    return render_template('index.html')

@app.route('/data')
def get_data():
    try:
        response = requests.get('http://localhost:5001/latest-data')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch latest data from server: {response.status_code}")
            return jsonify({"error": f"Failed to fetch latest data from server: {response.status_code}"})
    except Exception as e:
        print(f"Error in get_data endpoint: {str(e)}")
        return jsonify({"error": str(e), "message": "Sensor tidak terbaca"})

@app.route('/latest-data')
def get_latest_data():
    try:
        db_connection = mysql.connector.connect(**db_config)
        cursor = db_connection.cursor()
        query = "SELECT sensor_value, reading_time, status FROM readings ORDER BY reading_time DESC LIMIT 1"
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            value, current_time, status = row
            data = {"value": format(value, '.2f'), "time": current_time.strftime('%Y-%m-%d %H:%M:%S'), "status": status}
            print(f"Sending latest data to website: {data}")
            return jsonify(data)
        else:
            print("No valid sensor data available.")
            return jsonify({"error": "No valid sensor data available", "message": "Sensor tidak terbaca"})
    except mysql.connector.Error as err:
        print(f"Error in get_latest_data endpoint: {str(err)}")
        return jsonify({"error": str(err), "message": "Sensor tidak terbaca"})
    finally:
        cursor.close()
        db_connection.close()

@app.route('/form')
def form():
    print("Rendering form.html")
    return render_template('form.html')

@app.route('/history-data')
def history_data():
    try:
        db_connection = mysql.connector.connect(**db_config)
        cursor = db_connection.cursor(dictionary=True)
        query = "SELECT sensor_value as value, reading_time as time, status FROM readings ORDER BY reading_time DESC LIMIT 100"
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db_connection.close()
        return jsonify(results)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err), "message": "Gagal mengambil data dari database"})

@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    data = request.json
    value = data.get('value')
    current_time = data.get('time')
    status = data.get('status')

    try:
        db_connection = mysql.connector.connect(**db_config)
        cursor = db_connection.cursor()
        query = "INSERT INTO readings (sensor_value, reading_time, status) VALUES (%s, %s, %s)"
        cursor.execute(query, (value, current_time, status))
        db_connection.commit()
        cursor.close()
        db_connection.close()
        return jsonify({"message": "Data berhasil disimpan ke database"})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err), "message": "Gagal menyimpan data ke database"})

if __name__ == '__main__':
    sensor_thread = threading.Thread(target=read_sensor)
    store_thread = threading.Thread(target=store_data)
    sensor_thread.start()
    store_thread.start()
    try:
        app.run(debug=True, port=5001, host='0.0.0.0')
    except KeyboardInterrupt:
        print("Stopping server...")
        sensor_thread.join()
        store_thread.join()
