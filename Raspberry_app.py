from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import json
import threading
import time

with open('config.json') as config_file:
    config = json.load(config_file)

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setup(config['alarm_pin'], GPIO.OUT)  
GPIO.setup(config['alert_pin'], GPIO.OUT)  
GPIO.setup(config['buzzer_pin'], GPIO.OUT)  
GPIO.setup(config['yellow_led_pin'], GPIO.OUT)  

stop_threads = False

def blink_yellow_led():
    global stop_threads
    while not stop_threads:
        GPIO.output(config['yellow_led_pin'], GPIO.HIGH)
        time.sleep(1)
        GPIO.output(config['yellow_led_pin'], GPIO.LOW)
        time.sleep(1)

def blink_buzzer():
    global stop_threads
    while not stop_threads:
        GPIO.output(config['buzzer_pin'], GPIO.HIGH)
        time.sleep(1)
        GPIO.output(config['buzzer_pin'], GPIO.LOW)
        time.sleep(1)

yellow_led_thread = None
buzzer_thread = None

def control_hardware(value):
    global yellow_led_thread, buzzer_thread, stop_threads

    stop_threads = False

    if value < 8.0:
        GPIO.output(config['alert_pin'], GPIO.HIGH) 
        GPIO.output(config['alarm_pin'], GPIO.LOW)  
        GPIO.output(config['yellow_led_pin'], GPIO.LOW)
        GPIO.output(config['buzzer_pin'], GPIO.LOW) 
        stop_threads = True
        if yellow_led_thread:
            yellow_led_thread.join()
            yellow_led_thread = None
        if buzzer_thread:
            buzzer_thread.join()
            buzzer_thread = None

    elif 8.0 <= value <= 10.0:
        GPIO.output(config['alert_pin'], GPIO.LOW)
        GPIO.output(config['alarm_pin'], GPIO.LOW) 
        if not yellow_led_thread:
            yellow_led_thread = threading.Thread(target=blink_yellow_led)
            yellow_led_thread.start()
        if not buzzer_thread:
            buzzer_thread = threading.Thread(target=blink_buzzer)
            buzzer_thread.start()

    else:
        GPIO.output(config['alert_pin'], GPIO.LOW)   
        GPIO.output(config['alarm_pin'], GPIO.HIGH)  
        GPIO.output(config['yellow_led_pin'], GPIO.LOW)  
        stop_threads = True
        if yellow_led_thread:
            yellow_led_thread.join()
            yellow_led_thread = None
        if not buzzer_thread:
            buzzer_thread = threading.Thread(target=blink_buzzer)
            buzzer_thread.start()

@app.route('/receive-data', methods=['POST'])
def receive_data():
    data = request.json
    value = data.get('value')
    status = data.get('status')

    if value is not None:
        control_hardware(value)
        return jsonify({"message": "Data received and processed successfully"}), 200
    else:
        return jsonify({"message": "Invalid data"}), 400

if _name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=9091)
    except KeyboardInterrupt:
        GPIO.cleanup()