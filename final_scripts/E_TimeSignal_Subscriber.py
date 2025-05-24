import logging
import paho.mqtt.client as mqtt
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd1in54

# === Logging Configuration ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === MQTT Configuration ===
MQTT_HOST = "192.168.1.42"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/timeSignal"

# === E-Ink Display Setup ===
epd = epd1in54.EPD()
epd.init()
epd.Clear(0xFF)
font = ImageFont.load_default()

def display_status(status_text):
    try:
        time_str = datetime.now().strftime("%H:%M")
        image = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image)
        draw.text((10, 30), f"Uhrzeit: {time_str}", font=font, fill=0)
        draw.text((10, 50), f"Pumpe: {status_text}", font=font, fill=0)
        epd.display(epd.getbuffer(image))
        logging.info(f"Display aktualisiert: {status_text}")
    except Exception as e:
        logging.error(f"Fehler beim Anzeigen: {e}")

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
        display_status('EIN' if payload=='ein' else 'AUS')
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
    epd.sleep()
