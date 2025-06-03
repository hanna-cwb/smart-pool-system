import time
import pigpio
import paho.mqtt.client as mqtt
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# DHT11-Sensor-Klasse für pigpio
class DHT11:
    def __init__(self, pi, gpio):
        self.pi = pi
        self.gpio = gpio
        self._cb = None
        self._humidity = None
        self._temperature = None

    def read(self):
        import dht11
        sensor = dht11.DHT11(pin=self.gpio)
        result = sensor.read()
        if result.is_valid():
            self._humidity = result.humidity
            self._temperature = result.temperature
            return self._humidity, self._temperature
        else:
            return None, None

# MQTT-Konfiguration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_TOPIC = "/sensor/temperature"
MQTT_USERNAME = "mqtt-user"
MQTT_PASSWORD = "mqtt"

# MQTT-Client vorbereiten
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("MQTT-Verbindung erfolgreich.")
    else:
        logging.error(f"MQTT-Verbindung fehlgeschlagen, Code: {rc}")

client.on_connect = on_connect
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()

# DHT11 Sensor vorbereiten
pi = pigpio.pi()
if not pi.connected:
    logging.error("pigpio daemon nicht verbunden.")
    exit()

DHT_GPIO = 4

# Du kannst alternativ auch das `dht11` Modul direkt verwenden:
try:
    import dht11
    sensor = dht11.DHT11(pin=DHT_GPIO)

    while True:
        result = sensor.read()
        if result.is_valid():
            temp = result.temperature
            hum = result.humidity
            logging.info(f"Messung: {temp} °C, {hum}%")
            client.publish(MQTT_TOPIC, f"{temp:.1f}")
        else:
            logging.warning("Messung ungültig.")
        time.sleep(10)

except KeyboardInterrupt:
    logging.info("Beendet durch Benutzer.")
finally:
    client.loop_stop()
    client.disconnect()
    pi.stop()