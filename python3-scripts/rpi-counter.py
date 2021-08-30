import RPi.GPIO as GPIO
import hub2hub
import time

pin = 35
i = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    if GPIO.input(pin) == False:
        hub2hub.transmit(i, 'ABC', str(i))
        i += 1
    time.sleep(0.1)

GPIO.cleanup()
