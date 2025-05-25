import Adafruit_DHT
import time
import paho.mqtt.client as mqtt
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Sensor-Konfiguration
SENSOR_TYPE = Adafruit_DHT.DHT11
GPIO_PIN = 4  # GPIO4 = Pin 7

# MQTT-Konfiguration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/temperature"

# MQTT-Callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("MQTT-Verbindung erfolgreich.")
    else:
        logging.error(f"MQTT-Verbindung fehlgeschlagen, Rückgabecode {rc}")

def on_publish(client, userdata, mid):
    logging.info("Temperatur erfolgreich gesendet.")

# MQTT-Client initialisieren
mqttc = mqtt.Client()
mqttc.username_pw_set(username="mqtt-user", password="mqtt")
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_start()

    humidity, temperature = Adafruit_DHT.read_retry(SENSOR_TYPE, GPIO_PIN)

    if temperature is not None:
        message = f"{temperature:.1f}"
        logging.info(f"Temperatur wird gesendet: {message} °C")
        mqttc.publish(MQTT_TOPIC, message)
    else:
        logging.warning("Sensor konnte keine Temperatur liefern.")

    time.sleep(10)

except KeyboardInterrupt:
    logging.info("Abbruch durch Benutzer.")
finally:
    mqttc.loop_stop()
    mqttc.disconnect()