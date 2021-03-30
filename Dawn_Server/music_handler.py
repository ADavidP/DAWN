import os
import time
import RPi.GPIO as GPIO

# GPIO output pins for various relays
RADIO = 7
LIVING_STARBOARD = 8
LIVING_PORT = 25
BEDROOM_PORT = 24
BEDROOM_STARBOARD = 23


class MusicHandler:

    radio_stations = {
        b'fip': 1,
        b'fip_electro': 2,
        b'triplej': 3,
        b'folk_forward': 4,
        b'gaydio': 5,
        b'bbc6': 6
    }

    def __init__(self):
        # Volume is scale of 0 to 6
        self.volume = 6
        self.radio_client_on = False
        self.spotify_client_on = False
        self.time_of_last_radio_toggle = None
        self.station = 0
        self.setup_gpio()
        self.stop_radio()
        self.stop_spotify()

    @staticmethod
    def is_thing_on(thing):
        radio_on = GPIO.input(RADIO)
        if not radio_on:
            return False
        else:
            if thing == 'bedroom':
                return GPIO.input(BEDROOM_PORT)
            elif thing == 'living':
                return GPIO.input(LIVING_PORT)
            elif thing == 'radio':
                return GPIO.input(RADIO)

    def start_spotify(self):
        self.spotify_client_on = True
        os.system('sudo systemctl start raspotify')

    def stop_spotify(self):
        self.spotify_client_on = False
        os.system('sudo systemctl stop raspotify')

    def toggle_spotify(self):
        if self.spotify_client_on:
            self.stop_spotify()
        else:
            self.start_spotify()

    def play_radio(self, station):
        if self.radio_stations[station] == self.station:
            self.stop_radio()
        else:
            os.system('mpc play {}'.format(self.radio_stations[station]))
            self.radio_client_on = True
            self.station = self.radio_stations[station]

    def stop_radio(self):
        os.system('mpc stop')
        self.radio_client_on = False
        self.station = 0

    def set_volume(self, v):
        if 0 <= v <= 6:
            self.volume = v
            os.system('amixer sset PCM,0 {}\%'.format(70 + self.volume * 5))

    def volume_up(self):
        self.set_volume(self.volume + 1)

    def volume_down(self):
        self.set_volume(self.volume - 1)

    @staticmethod
    def setup_gpio():
        GPIO.setup(RADIO, GPIO.OUT, initial=False)
        GPIO.setup(LIVING_STARBOARD, GPIO.OUT, initial=True)
        GPIO.setup(LIVING_PORT, GPIO.OUT, initial=True)
        GPIO.setup(BEDROOM_PORT, GPIO.OUT, initial=True)
        GPIO.setup(BEDROOM_STARBOARD, GPIO.OUT, initial=True)

    @staticmethod
    def toggle_thing(pin):
        GPIO.output(pin, not GPIO.input(pin))

    def toggle_bedroom(self):
        self.toggle_thing(BEDROOM_PORT)
        self.toggle_thing(BEDROOM_STARBOARD)

    def toggle_livingroom(self):
        self.toggle_thing(LIVING_PORT)
        self.toggle_thing(LIVING_STARBOARD)

    def toggle_radio(self):
        current_time = time.time()
        if (self.time_of_last_radio_toggle is None or
                current_time - self.time_of_last_radio_toggle > 15):
            self.time_of_last_radio_toggle = current_time
            if GPIO.input(RADIO):
                self.turn_radio_off()
            else:
                self.turn_radio_on()

    def turn_radio_off(self):
        if self.spotify_client_on:
            self.stop_spotify()
        if self.radio_client_on:
            self.stop_radio()

        # set all to True to save power
        GPIO.output(LIVING_STARBOARD, True)
        GPIO.output(LIVING_PORT, True)
        GPIO.output(BEDROOM_PORT, True)
        GPIO.output(BEDROOM_STARBOARD, True)
        GPIO.output(RADIO, False)

    @staticmethod
    def turn_radio_on():
        # do living room by default
        GPIO.output(LIVING_STARBOARD, True)
        GPIO.output(LIVING_PORT, True)
        GPIO.output(BEDROOM_PORT, False)
        GPIO.output(BEDROOM_STARBOARD, False)
        GPIO.output(RADIO, True)
