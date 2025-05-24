import time
from datetime import datetime
import logging
import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd1in54

# === Logging Configuration ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === MQTT Configuration ===
MQTT_HOST = "192.168.1.42"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/timeSignal"

# === Time Schedule: (HH:MM, Duration in Minutes)
PUMP_SCHEDULE = [("08:00", 2), ("18:00", 2)]

# === E-Ink Display Setup ===
epd = epd1in54.EPD()
epd.init()
epd.Clear(0xFF)
font = ImageFont.load_default()

def display_status(time_str, status_text):
    try:
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
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    logging.info("Message Published successfully")

# === Main Code ===
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_start()

    pumpe_aktiv = False
    startzeit = None

    logging.info("Time Signal Publisher gestartet.")

    while True:
        jetzt = datetime.now()
        aktuelle_zeit = jetzt.strftime("%H:%M")

        for start, dauer in PUMP_SCHEDULE:
            if aktuelle_zeit == start and not pumpe_aktiv:
                pumpe_aktiv = True
                startzeit = jetzt
                logging.info(f"Pumpe EIN ({aktuelle_zeit})")
                mqttc.publish(MQTT_TOPIC, "ein")
                display_status(aktuelle_zeit, "EIN")

        if pumpe_aktiv and (datetime.now() - startzeit).seconds >= dauer * 60:
            pumpe_aktiv = False
            aktuelle_zeit = datetime.now().strftime("%H:%M")
            logging.info(f"Pumpe AUS ({aktuelle_zeit})")
            mqttc.publish(MQTT_TOPIC, "aus")
            display_status(aktuelle_zeit, "AUS")

        time.sleep(10)

except Exception as e:
    logging.error(f"MQTT Error: {e}")
    mqttc.loop_stop()
    epd.sleep()
