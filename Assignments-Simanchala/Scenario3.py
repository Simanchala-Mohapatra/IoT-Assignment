# Scenario 3: Smart Agriculture
# Question:
# Developed an IOT system for monitoring soil moisture and temperature in a farm and send alerts to farmers
# when irrigation is needed.
# Programming focus:Sensors, Arduino/Raspberry Pi, Communication Protocols(e.g. LoRaWan, Sigfox), cloud platform
# (e.g. AWS IoT, Azure IoT), data visualization
# Question:
# Write a python script that reads data from a soil moisture sensor uses a machine learning model to predict irrigation
# needs and sends a notification to a user's mobile app.
# Programming focus: python, machine learning libraries(e.g. scikit-learn, tensorflow), sensor libraries, cloud services
# (e.g. AWS, Azure, Google Cloud)


import time
import numpy as np
import random
from datetime import datetime, timedelta
import os

class MockIrrigationModel:
    def predict_proba(self, features):
        """
        Simple mock model that returns probability based on moisture level
        Lower moisture = higher probability of needing irrigation
        """
        moisture = features[0][0]
        if moisture < 30:
            return np.array([[0.2, 0.8]])
        elif moisture < 50:
            return np.array([[0.5, 0.5]])
        else:
            return np.array([[0.9, 0.1]])


MOISTURE_THRESHOLD = 40
SENSOR_ID = "soil_sensor_1"
FARM_LOCATION = "Field A"
HISTORY_LENGTH = 24

model = MockIrrigationModel()

sensor_history = []
last_irrigation_time = datetime.now() - timedelta(hours=23)


def simulate_sensor_reading():
    """Generate simulated sensor data"""
    hours_since_irrigation = (datetime.now() - last_irrigation_time).total_seconds() / 3600
    base_moisture = max(10, 80 - (hours_since_irrigation * 2))
    moisture = base_moisture + random.uniform(-5, 5)

    soil_temp = 22 + random.uniform(-3, 3)
    air_temp = 25 + random.uniform(-5, 5)
    humidity = 60 + random.uniform(-10, 10)
    rainfall = 0
    if random.random() < 0.1:
        rainfall = random.uniform(0, 5)

    return {
        'timestamp': datetime.now().isoformat(),
        'moisture': round(moisture, 1),
        'soil_temp': round(soil_temp, 1),
        'air_temp': round(air_temp, 1),
        'humidity': round(humidity, 1),
        'rainfall': round(rainfall, 1)
    }


def send_notification(message):
    """Simulate sending a notification by printing to console and logging to file"""
    print("\n" + "=" * 50)
    print("NOTIFICATION SENT TO MOBILE APP:")
    print(message)
    print("=" * 50 + "\n")

    with open('data/notifications.log', 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")


def predict_irrigation_need(moisture, temperature, humidity, last_irrigation_hours, rainfall_last_24h):
    """
    Use the mock ML model to predict if irrigation is needed
    Returns: (irrigation_needed (bool), confidence (float))
    """
    features = np.array([[
        moisture,
        temperature,
        humidity,
        last_irrigation_hours,
        rainfall_last_24h
    ]])

    probability = model.predict_proba(features)[0][1]
    needs_irrigation = probability > 0.7

    return needs_irrigation, probability


def process_sensor_data(sensor_data):
    """Process sensor data and determine irrigation needs"""
    try:
        moisture = sensor_data['moisture']
        soil_temp = sensor_data['soil_temp']
        air_temp = sensor_data['air_temp']
        humidity = sensor_data['humidity']
        rainfall = sensor_data['rainfall']
        timestamp = sensor_data['timestamp']

        print(
            f"Sensor data - Moisture: {moisture}%, Soil Temp: {soil_temp}°C, Air Temp: {air_temp}°C, Humidity: {humidity}%, Rainfall: {rainfall}mm")

        hours_since_irrigation = (datetime.now() - last_irrigation_time).total_seconds() / 3600

        sensor_history.append(sensor_data)

        if len(sensor_history) > HISTORY_LENGTH:
            sensor_history.pop(0)

        rainfall_last_24h = sum(point['rainfall'] for point in sensor_history)

        irrigation_needed, confidence = predict_irrigation_need(
            moisture,
            soil_temp,
            humidity,
            hours_since_irrigation,
            rainfall_last_24h
        )

        with open('data/sensor_readings.csv', 'a') as f:
            if os.stat('data/sensor_readings.csv').st_size == 0:
                f.write("timestamp,moisture,soil_temp,air_temp,humidity,rainfall,irrigation_needed,confidence\n")
            f.write(
                f"{timestamp},{moisture},{soil_temp},{air_temp},{humidity},{rainfall},{irrigation_needed},{confidence}\n")

        if irrigation_needed:
            notification_message = (
                f"Irrigation Alert: Field {FARM_LOCATION} needs irrigation.\n"
                f"Current moisture: {moisture}%\n"
                f"Soil temperature: {soil_temp}°C\n"
                f"Prediction confidence: {confidence * 100:.1f}%"
            )
            send_notification(notification_message)
            return True
        else:
            print(f"No irrigation needed. Moisture: {moisture}%, Confidence: {confidence * 100:.1f}%")
            return False

    except Exception as e:
        print(f"Error processing sensor data: {e}")
        return False


def main():
    """Main function to run the smart irrigation system"""
    global last_irrigation_time

    print("Starting Smart Agriculture Irrigation System (Simulation)")
    print("Press Ctrl+C to stop the system")

    if not os.path.exists('data/sensor_readings.csv'):
        with open('data/sensor_readings.csv', 'w') as f:
            f.write("timestamp,moisture,soil_temp,air_temp,humidity,rainfall,irrigation_needed,confidence\n")

    if not os.path.exists('data/notifications.log'):
        open('data/notifications.log', 'w').close()

    try:
        cycle = 0
        while True:
            print(f"\nSimulation cycle: {cycle}")
            sensor_data = simulate_sensor_reading()

            irrigation_triggered = process_sensor_data(sensor_data)

            if irrigation_triggered:
                last_irrigation_time = datetime.now()
                print(f"Irrigation performed at {last_irrigation_time}")

            cycle += 1
            print(f"Next reading in 5 seconds...")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping smart irrigation system simulation...")
    finally:
        print("System terminated. Data saved in the 'data' directory.")


if __name__ == "__main__":
    main()