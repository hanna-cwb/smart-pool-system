import time
from datetime import datetime
import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd1in54

# MQTT Setup
MQTT_BROKER = "localhost"  # oder IP vom Pi z. B. "192.168.1.42"
MQTT_PORT = 1883
MQTT_TOPIC = "pool/pumpe"

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Zeitpläne: Uhrzeit (HH:MM), Dauer in Minuten
pump_schedule = [("08:00", 2), ("18:00", 2)]

pumpe_aktiv = False
startzeit = None

# E-Paper Setup
epd = epd1in54.EPD()
epd.init()
epd.Clear(0xFF)
font = ImageFont.load_default()

# Funktion: Anzeige aktualisieren
def display_status(uhrzeit, status_text):
    try:
        image = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image)

        draw.text((10, 30), f"Uhrzeit: {uhrzeit}", font=font, fill=0)
        draw.text((10, 50), f"Pumpe: {status_text}", font=font, fill=0)

        epd.display(epd.getbuffer(image))
    except Exception as e:
        print("Display-Fehler:", e)

print("Time Signal läuft (eigenständig)...")

while True:
    jetzt = datetime.now()
    aktuelle_zeit = jetzt.strftime("%H:%M")

    for start, dauer in pump_schedule:
        if aktuelle_zeit == start and not pumpe_aktiv:
            pumpe_aktiv = True
            startzeit = jetzt
            print(f"[{aktuelle_zeit}] → Pumpe EIN")
            client.publish(MQTT_TOPIC, "ein")
            display_status(aktuelle_zeit, "EIN")

    if pumpe_aktiv and (datetime.now() - startzeit).seconds >= dauer * 60:
        pumpe_aktiv = False
        aktuelle_zeit = datetime.now().strftime("%H:%M")
        print(f"[{aktuelle_zeit}] → Pumpe AUS")
        client.publish(MQTT_TOPIC, "aus")
        display_status(aktuelle_zeit, "AUS")

    time.sleep(10)

    #mosquitto_sub -t pool/pumpe