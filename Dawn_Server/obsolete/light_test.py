import time

import RPi.GPIO as GPIO

import warm_glow

BEDROOM_LIGHTS_RELAY = 18
LIVING_ROOM_LIGHTS_RELAY = 15
GPIO.setmode(GPIO.BCM)
GPIO.setup(BEDROOM_LIGHTS_RELAY, GPIO.OUT)
GPIO.setup(LIVING_ROOM_LIGHTS_RELAY, GPIO.OUT)

def enable_lights_relay():
    GPIO.output(BEDROOM_LIGHTS_RELAY, False)
    GPIO.output(LIVING_ROOM_LIGHTS_RELAY, False)
    time.sleep(0.002)
    warm_glow.kill_all()

def disable_lights_relay():
    GPIO.output(BEDROOM_LIGHTS_RELAY, True)
    GPIO.output(LIVING_ROOM_LIGHTS_RELAY, True)


disable_lights_relay()
time.sleep(3)

enable_lights_relay()

time.sleep(3)

warm_glow.toggle_living_room_lights()

time.sleep(3)

warm_glow.toggle_living_room_lights()
