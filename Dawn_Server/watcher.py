import os
import time
import threading
import RPi.GPIO as GPIO
from music_handler import MusicHandler
from light_handler import LightHandler

RECOGNISED_PHONE_IPS = ['192.168.1.213',  # Parsons Fairphone
                        '192.168.1.130']  # Sophs Fairphone
SENSOR = 16

class PhoneWatch:
    light_handler = ...  # type: LightHandler
    music_handler = ...  # type: MusicHandler

    def __init__(self, music_handler, light_handler):
        GPIO.setup(SENSOR, GPIO.IN)
        self.music_handler = music_handler
        self.light_handler = light_handler
        self.had_connection_before = True
        self.is_anyone_home = True

    def returned_home(self):
        for i in range(300):
            if GPIO.input(SENSOR):
                self.light_handler.toggle_kitchen_lights()
                self.light_handler.set_brightness(1)
                break
            else:
                time.sleep(2)

    def watch(self):
        while True:
            if self.is_anyone_home:
                time.sleep(30 * 60)
                any_phones_found = False
                for ip in RECOGNISED_PHONE_IPS:
                    response = os.system("ping -c 1 " + ip)
                    # and then check the response...
                    if response == 0:
                        any_phones_found = True
                        break
                if any_phones_found:
                    self.had_connection_before = True
                else:
                    if not self.had_connection_before:
                        self.music_handler.turn_radio_off()
                        self.light_handler.kill_all()
                        self.is_anyone_home = False
                    self.had_connection_before = False
            else:
                time.sleep(30)
                any_phones_found = False
                for ip in RECOGNISED_PHONE_IPS:
                    response = os.system("ping -c 1 " + ip)
                    # and then check the response...
                    if response == 0:
                        any_phones_found = True
                        break
                if any_phones_found:
                    self.is_anyone_home = True
                    check_for_movement = threading.Thread(target=self.returned_home)
                    check_for_movement.start()


