import time
import datetime
from music_handler import MusicHandler
from warm_glow import LightHandler


class AlarmWatch:
    light_handler = ...  # type: LightHandler
    music_handler = ...  # type: MusicHandler

    def __init__(self, music_handler, light_handler):
        self.weekday_alarm_time = None
        self.weekend_alarm_time = None
        self.music_handler = music_handler
        self.light_handler = light_handler

    def set_alarm(self, alarm_string):
        alarm_type = alarm_string.split('#')[1]
        alarm_time = [int(a) for a in alarm_string.split('#')[2].split(':')]
        if alarm_type == 'MF':
            self.weekday_alarm_time = datetime.time(*alarm_time)
        elif alarm_type == 'SS':
            self.weekend_alarm_time = datetime.time(*alarm_time)

    def clear_alarm(self, alarm_string):
        alarm_type = alarm_string.split('#')[1]
        if alarm_type == 'MF':
            self.weekday_alarm_time = None
        elif alarm_type == 'SS':
            self.weekend_alarm_time = None

    def alarm_watch(self):
        while True:
            time.sleep(60)
            current_datetime = datetime.datetime.now()
            if 0 <= current_datetime.weekday() <= 4 and self.weekday_alarm_time is not None:
                alarm_of_interest = self.weekday_alarm_time
            elif 5 <= current_datetime.weekday() <= 6 and self.weekend_alarm_time is not None:
                alarm_of_interest = self.weekend_alarm_time
            else:
                continue
            kick_off_time = (datetime.datetime.combine(datetime.date(1, 1, 1), alarm_of_interest) -
                             datetime.timedelta(minutes=3)).time()
            if (current_datetime.hour == kick_off_time.hour and
                    current_datetime.minute == kick_off_time.minute):
                self.initiate_alarm()

    def initiate_alarm(self):
        self.music_handler.set_volume(0)
        self.music_handler.turn_radio_on()
        self.music_handler.toggle_bedroom()
        self.music_handler.play_radio(b'bbc6')
        for i in range(7):
            b = (i + 1)/28.0
            if self.light_handler.br_on or i == 0:
                self.light_handler.br_on = True
                self.light_handler.set_brightness(b)
            if self.music_handler.is_thing_on('radio') or i == 0:
                self.music_handler.volume_up()
            if self.light_handler.br_on or i == 0 or self.music_handler.is_thing_on('radio'):
                time.sleep(60)
