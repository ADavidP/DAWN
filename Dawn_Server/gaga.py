import RPi.GPIO as GPIO
import music_handler


RADIO = 7
LIVING_STARBOARD = 8
LIVING_PORT = 25
BEDROOM_PORT = 24
BEDROOM_STARBOARD = 23
WIFI = 14


def setup_gpio():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(RADIO, GPIO.OUT, initial=True)
    GPIO.setup(LIVING_STARBOARD, GPIO.OUT, initial=True)
    GPIO.setup(LIVING_PORT, GPIO.OUT, initial=True)
    GPIO.setup(BEDROOM_PORT, GPIO.OUT, initial=True)
    GPIO.setup(BEDROOM_STARBOARD, GPIO.OUT, initial=True)

def toggle_thing(pin):
    GPIO.output(pin, not GPIO.input(pin))


def toggle_bedroom():
    toggle_thing(BEDROOM_PORT)
    toggle_thing(BEDROOM_STARBOARD)


def toggle_livingroom():
    toggle_thing(LIVING_PORT)
    toggle_thing(LIVING_STARBOARD)


def toggle_radio():
    if GPIO.input(RADIO):
        turn_radio_off()
    else:
        turn_radio_on()


def turn_radio_off():
    music_handler.stop_spotify()

    # set all to True to save power
    GPIO.output(LIVING_STARBOARD, True)
    GPIO.output(LIVING_PORT, True)
    GPIO.output(BEDROOM_PORT, True)
    GPIO.output(BEDROOM_STARBOARD, True)

    GPIO.output(RADIO, False)


def turn_radio_on():
    # do living room by default
    GPIO.output(LIVING_STARBOARD, True)
    GPIO.output(LIVING_PORT, True)
    GPIO.output(BEDROOM_PORT, False)
    GPIO.output(BEDROOM_STARBOARD, False)
    GPIO.output(RADIO, True)


def radio_pin_off():
    GPIO.output(RADIO, False)
