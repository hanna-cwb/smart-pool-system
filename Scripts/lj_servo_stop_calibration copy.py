import time
import board
import busio
from adafruit_pca9685 import PCA9685

# I2C-Initialisierung
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x41)
pca.frequency = 50

# Servo-Kanal
servo = pca.channels[1]

# Hilfsfunktion zur Pulsbreitensteuerung in µs
def set_servo_pulse_us(channel, pulse_us):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= pca.frequency  # us per period (should be 20000 us)
    pulse_scale = 65535 / pulse_length
    pwm_value = int(pulse_us * pulse_scale)
    channel.duty_cycle = pwm_value

print("Kalibrierung gestartet. Teste verschiedene µs-Werte (Stop liegt meist zwischen 1450–1550 µs)...")

try:
    for us in range(1450, 1560, 5):
        print(f"Teste Puls: {us} µs")
        set_servo_pulse_us(servo, us)
        time.sleep(2)
        set_servo_pulse_us(servo, 1500)  # Zurück auf neutral nach jedem Schritt
        time.sleep(0.5)
    print("Kalibrierung abgeschlossen.")
except KeyboardInterrupt:
    print("Abbruch durch Benutzer.")
finally:
    #set_servo_pulse_us(servo, 1500)
    servo.duty_cycle = 0x0000  # Neutral
    pca.deinit()
    print("Servo gestoppt und PWM deaktiviert.")