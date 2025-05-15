import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
LED_PIN = 17
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    while True:
        eingabe = input("LED ein (1) / aus (0) / beenden (x): ").strip()
        if eingabe == "1":
            GPIO.output(LED_PIN, GPIO.HIGH)
            print("LED ist AN")
        elif eingabe == "0":
            GPIO.output(LED_PIN, GPIO.LOW)
            print("LED ist AUS")
        elif eingabe.lower() == "x":
            break
        else:
            print("Ungültige Eingabe.")
finally:
    GPIO.cleanup()
