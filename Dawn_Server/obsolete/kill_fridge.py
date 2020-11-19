import RPi.GPIO as GPIO

FRIDGE = 17

GPIO.setmode(GPIO.BCM)

GPIO.setup(FRIDGE, GPIO.OUT, initial=True)
GPIO.output(FRIDGE, True)
print 'fridge off'
