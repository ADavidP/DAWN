"""Module for handling control of music. Handles relays which turn on stereo and speakers, and act as interface to
command line for choice of spotify/online radio stations.
"""
import os
import time
import RPi.GPIO as GPIO

# GPIO output pins for various relays
STEREO = 7
LIVING_STARBOARD = 8
LIVING_PORT = 25
BEDROOM_PORT = 24
BEDROOM_STARBOARD = 23


class MusicHandler:
    """Overarching class for handling music"""

    # Mapping of radio station command from app to index in mpc list
    RADIO_STATIONS = {
        b'classic': 1,
        b'bbc2': 2,
        b'bbc_bristol': 3,
        b'bbc6': 4
    }

    def __init__(self):
        # Volume is scale of 0 to 6. Initialise at maximum.
        self.volume = 6
        self.radio_client_on = False
        self.spotify_client_on = False
        self.time_of_last_stereo_toggle = None
        self.station = 0
        self.setup_gpio()
        self.stop_radio()
        self.stop_spotify()

    @staticmethod
    def is_thing_on(thing):
        if GPIO.input(STEREO):
            # Stereo is on
            if thing == 'bedroom_speakers':
                return GPIO.input(BEDROOM_PORT)
            elif thing == 'living_room_speakers':
                return GPIO.input(LIVING_PORT)
            elif thing == 'stereo':
                return GPIO.input(STEREO)
        else:
            return False

    def start_spotify(self):
        self.stop_radio()
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
        self.stop_spotify()
        if self.RADIO_STATIONS[station] == self.station:
            self.stop_radio()
        else:
            os.system('mpc play {}'.format(self.RADIO_STATIONS[station]))
            self.radio_client_on = True
            self.station = self.RADIO_STATIONS[station]

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
        GPIO.setup(STEREO, GPIO.OUT, initial=False)
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

    def toggle_living_room(self):
        self.toggle_thing(LIVING_PORT)
        self.toggle_thing(LIVING_STARBOARD)

    def toggle_stereo(self):
        current_time = time.time()
        if (self.time_of_last_stereo_toggle is None or
                current_time - self.time_of_last_stereo_toggle > 8):
            self.time_of_last_stereo_toggle = current_time
            if GPIO.input(STEREO):
                self.turn_stereo_off()
            else:
                self.turn_stereo_on()

    def turn_stereo_off(self):
        if self.spotify_client_on:
            self.stop_spotify()
        if self.radio_client_on:
            self.stop_radio()

        # set all to True to save power
        GPIO.output(LIVING_STARBOARD, True)
        GPIO.output(LIVING_PORT, True)
        GPIO.output(BEDROOM_PORT, True)
        GPIO.output(BEDROOM_STARBOARD, True)
        GPIO.output(STEREO, False)

    @staticmethod
    def turn_stereo_on():
        # do living room by default
        GPIO.output(LIVING_STARBOARD, True)
        GPIO.output(LIVING_PORT, True)
        GPIO.output(BEDROOM_PORT, False)
        GPIO.output(BEDROOM_STARBOARD, False)
        GPIO.output(STEREO, True)
