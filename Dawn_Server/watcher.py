import os
import time
from music_handler import MusicHandler
from warm_glow import LightHandler

RECOGNISED_PHONE_IPS = ['192.168.1.213',  # Parsons Fairphone
                        '192.168.1.130']  # Sophs Fairphone

class PhoneWatch:
    light_handler = ...  # type: LightHandler
    music_handler = ...  # type: MusicHandler

    def __init__(self, music_handler, light_handler):
        self.music_handler = music_handler
        self.light_handler = light_handler
        self.had_connection_before = True

    def watch(self):
        while True:
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
                self.had_connection_before = False
