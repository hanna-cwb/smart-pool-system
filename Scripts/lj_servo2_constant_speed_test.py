import time
import board
import busio
from adafruit_pca9685 import PCA9685

# I2C-Bus und PCA9685 initialisieren (Adresse 0x41)
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x41)
pca.frequency = 50  # 50Hz = 20ms Periode

# Kanal für Servo
servo_channel = 1
servo = pca.channels[1]

# Hilfsfunktion: Pulsbreite in Mikrosekunden setzen
def set_servo_pulse(pca, channel, pulse_us):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= pca.frequency  # us per period
    pulse_scale = 65535 / pulse_length
    pwm_value = int(pulse_us * pulse_scale)
    pca.channels[channel].duty_cycle = pwm_value

try:
    print("Servo: konstante Rückwärtsbewegung für 2 Sekunden")
    set_servo_pulse(pca, servo_channel, 1500)
    time.sleep(2)

    print("Servo: Pause (2 Sekunden)")
    set_servo_pulse(pca, servo_channel, 1555)  # 1500 µs = neutral (Stop)
    time.sleep(2)
    
    print("Servo: konstante Vorwärtsbewegung für 2 Sekunden")
    set_servo_pulse(pca, servo_channel, 1600)
    time.sleep(2)
    
except KeyboardInterrupt:
    print("Abgebrochen mit STRG+C.")
finally:
    print("Servo: Stop")
    #set_servo_pulse(pca, servo_channel, 1550)  # Stop
    servo.duty_cycle = 0x0000
    pca.deinit()
    print("PWM deaktiviert.")