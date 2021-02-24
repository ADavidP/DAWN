import time

import RPi.GPIO as GPIO

# GPIO output pin for router relay
ROUTER = 14


class RouterHandler:
    def __init__(self):
        GPIO.setup(ROUTER, GPIO.OUT, initial=True)

    @staticmethod
    def reset_router():
        GPIO.output(ROUTER, False)
        time.sleep(10)
        GPIO.output(ROUTER, True)
