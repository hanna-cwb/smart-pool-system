import time
from datetime import datetime
import logging
import paho.mqtt.client as mqtt

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MQTT Configuration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/timeSignal"

# Time Schedule: (HH:MM, Duration in minutes)
PUMP_SCHEDULE = [("09:23", 2), ("09:24", 2)]

# Simulate Display-Output without GPIO/epd
def display_status(time_str, status_text):
    print(f"[DISPLAY SIMULATION] Time: {time_str} | Pump: {status_text}")

# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker successfully")
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    logging.info("Message Published successfully")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_start()

    pumpe_aktiv = False
    startzeit = None

    logging.info("Time Signal Publisher started.")

    while True:
        jetzt = datetime.now()
        aktuelle_zeit = jetzt.strftime("%H:%M")

        for start, dauer in PUMP_SCHEDULE:
            if aktuelle_zeit == start and not pumpe_aktiv:
                pumpe_aktiv = True
                startzeit = jetzt
                logging.info(f"Pump ON ({aktuelle_zeit})")
                mqttc.publish(MQTT_TOPIC, "on")
                display_status(aktuelle_zeit, "ON")

        if pumpe_aktiv and (datetime.now() - startzeit).seconds >= dauer * 60:
            pumpe_aktiv = False
            aktuelle_zeit = datetime.now().strftime("%H:%M")
            logging.info(f"Pump OFF ({aktuelle_zeit})")
            mqttc.publish(MQTT_TOPIC, "off")
            display_status(aktuelle_zeit, "OFF")

        time.sleep(10)

except KeyboardInterrupt:
    logging.info("Measurement stopped by user.")
except Exception as e:
    logging.error(f"MQTT Error: {e}")
finally:
    mqttc.loop_stop()
    mqttc.disconnect()