# Snenario 1: Smart home automation
# Question:
# You are developing a smart home system that allows users to control lights thermostats and door locks
# remotely designing system architecture including hardware components communication protocols and software components
# to achieve this functionality consider security and scalability.
# Programming focus: MQTT, REST, APIs, Cloud Services AWS, Azure, Google Cloud, Database design, device management
# Question:
# Implement a python script that reads temperature and humidity data from sensor stores it in a database and
# sends an alert to a user's phone with the temperature exceeds a sudden threshold.
# Programming focus:Python, sensor libraries, database interaction(e.g. SQLite, MySql), MQTT,
# Cloud services(e.g. AWSIot, Google cloud Iot)



import time
import sqlite3
import paho.mqtt.client as mqtt
import json
from datetime import datetime

TEMPERATURE_THRESHOLD = 30.0
HUMIDITY_THRESHOLD = 80.0
DB_NAME = 'sensor_data.db'
MQTT_BROKER = 'mqtt.eclipseprojects.io'
MQTT_TOPIC_PUBLISH = 'home/sensor/temperature'
MQTT_TOPIC_SUBSCRIBE = 'home/alert/notification'
SENSOR_INTERVAL = 15

def read_sensor_data():
    return {
        'temperature': 25.0 + (5 * (time.time() % 10) / 10),
        'humidity': 45.0 + (40 * (time.time() % 10) / 10),
        'timestamp': datetime.now().isoformat()
    }

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp TEXT NOT NULL,
            alert_sent INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def store_reading(temperature, humidity, timestamp):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_readings (temperature, humidity, timestamp)
        VALUES (?, ?, ?)
    ''', (temperature, humidity, timestamp))
    conn.commit()
    conn.close()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC_SUBSCRIBE)

def on_message(client, userdata, msg):
    print(f"Received message on {msg.topic}: {msg.payload.decode()}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.loop_start()

def send_alert(temperature, humidity):
    alert_message = {
        "alert": "Temperature/Humidity Alert",
        "message": f"Temperature {temperature}°C exceeds threshold {TEMPERATURE_THRESHOLD}°C" if temperature > TEMPERATURE_THRESHOLD else f"Humidity {humidity}% exceeds threshold {HUMIDITY_THRESHOLD}%",
        "timestamp": datetime.now().isoformat(),
        "values": {
            "temperature": temperature,
            "humidity": humidity
        }
    }

    mqtt_client.publish(MQTT_TOPIC_PUBLISH, json.dumps(alert_message))
    print(f"Alert sent: {alert_message}")

def monitor_sensors():
    init_db()
    
    while True:
        try:
            data = read_sensor_data()
            temp = data['temperature']
            hum = data['humidity']
            ts = data['timestamp']

            store_reading(temp, hum, ts)
            print(f"Stored reading: Temp={temp}°C, Hum={hum}%")

            mqtt_client.publish(MQTT_TOPIC_PUBLISH, json.dumps(data))

            if temp > TEMPERATURE_THRESHOLD or hum > HUMIDITY_THRESHOLD:
                send_alert(temp, hum)

            time.sleep(SENSOR_INTERVAL)
            
        except Exception as e:
            print(f"Error in monitoring: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_sensors()