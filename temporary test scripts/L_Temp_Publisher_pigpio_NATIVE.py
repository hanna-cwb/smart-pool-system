import time
import pigpio
import paho.mqtt.client as mqtt
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MQTT-Konfiguration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_TOPIC = "/sensor/temperature"
MQTT_USERNAME = "mqtt-user"
MQTT_PASSWORD = "mqtt"

# GPIO und Timing-Konstanten
DHT_PIN = 4  # GPIO4 = Pin 7

# Klasse zur DHT11-Datenverarbeitung über pigpio
class DHT11:
    def __init__(self, pi, gpio):
        self.pi = pi
        self.gpio = gpio
        self.cb = None

        self.humidity = None
        self.temperature = None

        self._new_data = False
        self._in_code = False
        self._edges = []
        self._tick = 0

        self.pi.set_mode(gpio, pigpio.INPUT)
        self.cb = self.pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    def _cbf(self, gpio, level, tick):
        if self._in_code:
            diff = pigpio.tickDiff(self._tick, tick)
            self._edges.append((level, diff))
        self._tick = tick

    def read(self):
        self._edges = []
        self._in_code = True
        self.pi.set_pull_up_down(self.gpio, pigpio.PUD_OFF)
        self.pi.set_mode(self.gpio, pigpio.OUTPUT)
        self.pi.write(self.gpio, 0)
        time.sleep(0.018)
        self.pi.set_mode(self.gpio, pigpio.INPUT)

        time.sleep(0.05)
        self._in_code = False

        # Auswertung der 40-Bit-Daten
        bits = []
        for i in range(2, len(self._edges), 2):
            if i+1 < len(self._edges):
                low, high = self._edges[i][1], self._edges[i+1][1]
                if low > 100 and high > 100:
                    bits.append(1 if high > 50 else 0)

        if len(bits) >= 40:
            data = []
            for i in range(0, 40, 8):
                byte = 0
                for j in range(8):
                    byte = (byte << 1) + bits[i + j]
                data.append(byte)

            checksum = (data[0] + data[1] + data[2] + data[3]) & 0xFF
            if data[4] == checksum:
                self.humidity = data[0]
                self.temperature = data[2]
                return True
        return False

# MQTT-Verbindung aufbauen
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

# pigpio initialisieren
pi = pigpio.pi()
if not pi.connected:
    logging.error("pigpiod nicht gestartet!")
    exit()

# Sensor auslesen und Temperatur senden
sensor = DHT11(pi, DHT_PIN)

try:
    while True:
        if sensor.read():
            temp = sensor.temperature
            hum = sensor.humidity
            logging.info(f"Temp: {temp} °C, Feuchte: {hum}%")
            client.publish(MQTT_TOPIC, f"{temp:.1f}")
        else:
            logging.warning("Sensor konnte nicht gelesen werden.")
        time.sleep(10)

except KeyboardInterrupt:
    logging.info("Abbruch durch Benutzer.")

finally:
    client.loop_stop()
    client.disconnect()
    pi.stop()