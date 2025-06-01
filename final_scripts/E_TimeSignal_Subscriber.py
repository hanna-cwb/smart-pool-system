import logging
import paho.mqtt.client as mqtt
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd1in54_V2

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MQTT Configuration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/timeSignal"

# E-Paper Display Setup
epd = epd1in54_V2.EPD()
epd.init(isPartial=False)
epd.Clear(0xFF)
font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 24)

def display_status(status_text):
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), f"Pumpstatus: {status_text}°C", font=font, fill=0)
    epd.display(epd.getbuffer(image))

# Simulate Display-Output without GPIO/epd
def display_statusSim(time_str, status_text):
    print(f"[DISPLAY SIMULATION] Time: {time_str} | Pump: {status_text}")

# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error(f"Connection failed with return code {rc}")

def on_subscribe(client, userdata, mid, granted_qos):
    logging.info(f"Subscribed to {MQTT_TOPIC} with QoS {granted_qos}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8').strip().lower()
    logging.info(f"Received Message: {payload}")
    if payload in ['on', 'off']:
        display_status('ON' if payload=='on' else 'OFF')
    else:
        logging.warning(f"Unknown payload: {payload}")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message

try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_forever()

except KeyboardInterrupt:
    logging.info("Measurement stopped by user.")
except Exception as e:
    logging.error(f"MQTT Error: {e}")
finally:
    mqttc.loop_stop()
    mqttc.disconnect()
