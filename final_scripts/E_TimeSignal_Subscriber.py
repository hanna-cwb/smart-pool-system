
import logging
import paho.mqtt.client as mqtt
from datetime import datetime

# === Logging Configuration ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === MQTT Configuration ===
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/timeSignal"


def display_status(time_str, status_text):
    # Simulierte Display-Ausgabe ohne GPIO/epd
    print(f"[DISPLAY SIMULATION] Uhrzeit: {time_str} | Pumpe: {status_text}")


# === MQTT Event Handlers ===
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker successfully")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_subscribe(client, userdata, mid, granted_qos):
    logging.info(f"Subscribed to {MQTT_TOPIC} with QoS {granted_qos}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8').strip().lower()
    logging.info(f"Received Message: {payload}")
    if payload in ['ein', 'aus']:
        display_status(datetime.now().strftime("%H:%M"), 'EIN' if payload=='ein' else 'AUS')
    else:
        logging.warning(f"Unknown payload: {payload}")

# === Main Code ===
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message

try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_forever()
except Exception as e:
    logging.error(f"MQTT Error: {e}")
