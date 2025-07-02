# Ludlum Monitoring

**DEVELOPMENT OF RADIATION MONITORING SYSTEM USING WEBSITE-BASED IoT WITH RASPBERRY PI AND LUDLUM 375**

![System Schematic](https://github.com/user-attachments/assets/ec9a6bb0-c860-4b62-8474-6150c138ba1e)

---

## Overview

Ludlum Monitoring is an integrated IoT system designed for real-time radiation monitoring using the Ludlum 375 sensor, a Raspberry Pi, and a web dashboard. The system reads ambient radiation levels and sends data to a central web server for visualization, alerting, and historical analysis.

**Key Features:**
- Real-time monitoring and visualization of radiation levels (µSv/hour)
- Automatic status indication with colored LEDs and buzzer alerts
- Historical data logging and web-based data display
- Robust communication between sensor, Raspberry Pi, and web server
- User-friendly dashboard with live chart and status indicators

---

## System Architecture

- **Ludlum 375 Sensor**: Measures radiation in the environment.
- **Raspberry Pi**: Acts as the IoT gateway, receiving sensor data and controlling hardware indicators (LEDs, buzzer).
- **Web Server (Flask)**: Collects data, stores it in a database, and serves a responsive dashboard.
- **Frontend**: Built with Bootstrap, Chart.js, and jQuery for live data and historical view.

### Data Flow

1. **Sensor Activation**: When powered on, the Ludlum sensor starts reading radiation.
2. **Data Transmission**: Sensor data is sent to the Raspberry Pi.
3. **Status Logic**: The Pi processes the data and triggers hardware indicators:
   - **Green LED**: Safe (<8 µSv/hour)
   - **Yellow LED + Buzzer**: Alert (8–10 µSv/hour)
   - **Red LED + Buzzer**: Danger (>10 µSv/hour)
4. **Web Synchronization**: Data is relayed to the Flask web backend, stored in a MySQL database, and displayed on the website.
5. **User Dashboard**: Users can view live readings, status, and historical logs via the web interface.

---

## Features

### Real-Time Dashboard

- **Live Chart**: Radiation values updated every 5 seconds.
- **Status Light**: Colored indicator lamp and text status ("SAFE", "ALERT", "DANGER").
- **History Table**: Scrollable table of previous readings with timestamps and statuses.

### Hardware Alerts

- **LEDs**: Green, yellow, and red LEDs indicate current radiation status.
- **Buzzer**: Sounds during alert and danger statuses.
- **Robust Control**: Hardware logic handled on the Raspberry Pi via GPIO.

### Fault Handling

- Automatic retries if sensor or transmission fails.
- Web interface shows "Sensor Not Read" if the sensor is disconnected or data is unavailable.

---

## Installation

### Requirements

- **Hardware**: Raspberry Pi (any modern model), Ludlum 375, LEDs, buzzer, wiring.
- **Software**:
  - Python 3.x
  - MySQL database
  - Required Python libraries (see `requirements.txt`)

### Setup Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/rafdi03/Ludlum_Monitoring.git
   cd Ludlum_Monitoring
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   - Create a MySQL database and table as follows:
     ```sql
     CREATE DATABASE radiation_monitoring;
     USE radiation_monitoring;
     CREATE TABLE readings (
       id INT AUTO_INCREMENT PRIMARY KEY,
       sensor_value FLOAT,
       reading_time DATETIME,
       status VARCHAR(10)
     );
     ```
   - Configure database credentials in your environment or configuration file.

4. **Configure Raspberry Pi GPIO**
   - Edit `config.json` for your GPIO pin numbers.

5. **Run the Web Server**
   ```bash
   python app.py
   ```
   - The web dashboard will be accessible on `http://<your_server_ip>:5001`

6. **Run the Raspberry Pi Controller**
   ```bash
   python Raspberry_app.py
   ```

---

## Usage

- Visit the main dashboard at `/` to monitor current radiation levels and see the status indicator.
- Access `/form` to manually input or adjust data (if enabled).
- The system will automatically log readings and alert if thresholds are exceeded.

---

## File Structure

- `app.py` — Main Flask application (web server, API, database logic)
- `Raspberry_app.py` — Raspberry Pi hardware controller (GPIO, data receiver)
- `requirements.txt` — Python dependencies
- `templates/` — HTML templates for web dashboard and forms
- `static/` — Static assets (CSS, JS)
- `static/js/updateDate.js` — Frontend logic for live data updates and charting
- `static/css/style.css` — Custom styles for dashboard

---

## Technologies Used

- **Backend**: Python, Flask, MySQL, pySerial, threading
- **Frontend**: Bootstrap, Chart.js, jQuery
- **IoT**: Raspberry Pi (GPIO control)
- **Hardware**: Ludlum 375, LEDs, buzzer

---

## Screenshots

![Dashboard Example](https://github.com/user-attachments/assets/ec9a6bb0-c860-4b62-8474-6150c138ba1e)

---

## Acknowledgements

- Developed as part of a research project for real-time radiation safety monitoring.
- Special thanks to all contributors and open source libraries used.

---

## License

This project is licensed under the MIT License.

---

## Contact

For questions, suggestions, or contributions, please create an issue or contact [rafdi03](https://github.com/rafdi03).
