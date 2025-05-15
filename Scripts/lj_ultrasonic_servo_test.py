import time
import board
import busio
import RPi.GPIO as GPIO
from adafruit_pca9685 import PCA9685

# Pins definieren
TRIG_PIN = 23
ECHO_PIN = 24

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# I2C & PCA9685 Setup
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x41)
pca.frequency = 50
servo_channel = 0

def set_servo_pulse(pca, channel, pulse_us):
    pulse_length = 1000000
    pulse_length //= pca.frequency
    pulse_scale = 65535 / pulse_length
    pwm_value = int(pulse_us * pulse_scale)
    pca.channels[channel].duty_cycle = pwm_value

def get_distance():
    # Trigger Impuls senden
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    # Warte auf Echo Start
    while GPIO.input(ECHO_PIN) == 0:
        start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        stop = time.time()

    # Berechne Distanz
    distance = (stop - start) * 34300 / 2
    return distance

try:
    while True:
        dist = get_distance()
        print(f"Distanz: {dist:.2f} cm")

        if dist < 10:  # zu wenig Wasser
            print("Wenig Wasser – Pumpe AN")
            set_servo_pulse(pca, servo_channel, 1600)  # vorwärts
        elif dist > 20:  # genug Wasser
            print("Genug Wasser – Pumpe AUS")
            set_servo_pulse(pca, servo_channel, 1500)  # stop
        else:
            print("Wasserstand ok – Pumpe LANGSAM")
            set_servo_pulse(pca, servo_channel, 1520)  # langsam drehen

        time.sleep(1)

except KeyboardInterrupt:
    print("Abbruch mit STRG+C")
finally:
    set_servo_pulse(pca, servo_channel, 1500)  # Stop
    pca.deinit()
    GPIO.cleanup()
