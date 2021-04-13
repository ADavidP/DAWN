"""Handles alarm functionality. Alarm time is changed through the app and stored in a persistent text file.
"""
import time
import datetime
from music_handler import MusicHandler
from light_handler import LightHandler


class AlarmWatch:
    light_handler = ...  # type: LightHandler
    music_handler = ...  # type: MusicHandler

    def __init__(self, music_handler, light_handler):
        with open("/home/pi/Dawn_Server/alarm_times.txt", 'r') as alarm_times:
            raw_weekday = alarm_times.readline()[:-1]
            raw_weekend = alarm_times.readline()[:-1]
        if raw_weekday == 'XX:XX':
            self.weekday_alarm_time = None
        else:
            alarm_time = [int(a) for a in raw_weekday.split(':')]
            self.weekday_alarm_time = datetime.time(*alarm_time)
        if raw_weekend == 'XX:XX':
            self.weekend_alarm_time = None
        else:
            alarm_time = [int(a) for a in raw_weekend.split(':')]
            self.weekend_alarm_time = datetime.time(*alarm_time)

        self.music_handler = music_handler
        self.light_handler = light_handler

    def set_alarm(self, alarm_string):
        alarm_type = alarm_string.split('#')[1]
        alarm_time = [int(a) for a in alarm_string.split('#')[2].split(':')]
        if alarm_type == 'MF':
            self.weekday_alarm_time = datetime.time(*alarm_time)
        elif alarm_type == 'SS':
            self.weekend_alarm_time = datetime.time(*alarm_time)
        self.store_alarms()

    def clear_alarm(self, alarm_string):
        alarm_type = alarm_string.split('#')[1]
        if alarm_type == 'MF':
            self.weekday_alarm_time = None
        elif alarm_type == 'SS':
            self.weekend_alarm_time = None
        self.store_alarms()

    def store_alarms(self):
        with open("/home/pi/Dawn_Server/alarm_times.txt", 'w') as alarm_times:
            if self.weekday_alarm_time is None:
                alarm_times.write("XX:XX")
            else:
                alarm_times.write(self.weekday_alarm_time.isoformat()[:-3])
            alarm_times.write("\n")

            if self.weekend_alarm_time is None:
                alarm_times.write("XX:XX")
            else:
                alarm_times.write(self.weekend_alarm_time.isoformat()[:-3])
            alarm_times.write("\n")

    def alarm_watch(self):
        while True:
            time.sleep(60)
            current_datetime = datetime.datetime.now()
            # Days indexed from 0 i.e. 0 -> 4 is equivalent to Monday to Friday
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
        self.music_handler.turn_stereo_on()
        # Turning stereo on only turns on living room speakers by default
        self.music_handler.toggle_bedroom()
        self.music_handler.play_radio(b'bbc6')
        self.light_handler.colour = self.light_handler.DEFAULT
        for i in range(7):
            b = (i + 1)/28.0
            if self.light_handler.bedroom_on or i == 0:
                self.light_handler.bedroom_on = True
                self.light_handler.set_brightness(b)
            if self.light_handler.bedroom_on or i == 0 or self.music_handler.is_thing_on('stereo'):
                time.sleep(60)
