import logging
import time
logging.info("1")
import paho.mqtt.client as mqtt
logging.info("2")
from PIL import Image, ImageDraw, ImageFont
logging.info("4")
from waveshare_epd import epd1in54_V2
logging.info("5")

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MQTT Configuration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/temperature"
logging.info("6")

# E-Paper Display Setup
epd = epd1in54_V2.EPD()
epd.init(isPartial=False)
epd.Clear(0xFF)
font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 24)
logging.info("7")

def display_temperature(temp_str):
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), f"Temp: {temp_str}°C", font=font, fill=0)
    epd.display(epd.getbuffer(image))

logging.info("8")
# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error(f"Connection failed with return code {rc}")

def on_subscribe(client, userdata, mid, granted_qos):
    logging.info(f"Subscribed to topic {MQTT_TOPIC}")

def on_message(client, userdata, msg):
    temp = msg.payload.decode()
    logging.info(f"Received temperature: {temp}°C")
    display_temperature(temp)
    time.sleep(2)


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
