import time
import RPi.GPIO as GPIO

SENSOR = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR, GPIO.IN)

time.sleep(2)

while True:
    print(GPIO.input(SENSOR))
    time.sleep(1)
