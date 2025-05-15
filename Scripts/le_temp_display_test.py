import time
import board
import adafruit_dht
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd1in54
import RPi.GPIO as GPIO

# GPIO-Pins für E-Ink Display
EPD_RST = 17
EPD_DC = 25
EPD_CS = 8      # Wird intern verwendet (SPI)
EPD_BUSY = 24

# Sensor initialisieren
dhtDevice = adafruit_dht.DHT11(board.D4)  # GPIO4

# Display initialisieren
epd = epd1in54.EPD()
epd.init()
epd.Clear(0xFF)

# Schriftart laden
font = ImageFont.load_default()

try:
    while True:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(f"Temperatur: {temperature} °C, Luftfeuchtigkeit: {humidity}%")

        # Bild vorbereiten
        image = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image)

        # Text zeichnen
        draw.text((10, 40), f"Temp: {temperature} °C", font=font, fill=0)
        draw.text((10, 70), f"Feuchte: {humidity} %", font=font, fill=0)

        # Bild anzeigen
        epd.display(epd.getbuffer(image))

        time.sleep(10)  # alle 10 Sekunden aktualisieren

except KeyboardInterrupt:
    print("Beendet")
    epd.sleep()
    GPIO.cleanup()