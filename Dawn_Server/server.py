"""Handles communication with clients."""
import threading

import socket
import music_handler
import light_handler
import router_handler
import alarm
import watcher
import RPi.GPIO as GPIO


def build_response(music_obj,  # type: music_handler.MusicHandler
                   lights_obj,  # type: light_handler.LightHandler
                   alarm_obj  # type: alarm.AlarmWatch
                   ):
    """Builds response to any message from app"""

    def add_colour(r, colour):
        for pigment in colour:
            r += pigment.to_bytes(1, 'big')
        return r

    def add_alarm_time(r, alarm_time):
        """Adds alarm time to response"""
        if alarm_time is None:
            r += False.to_bytes(1, 'big')
            r += (0).to_bytes(2, 'big')
        else:
            r += True.to_bytes(1, 'big')
            r += int(alarm_time.strftime("%H")).to_bytes(1, 'big')
            r += int(alarm_time.strftime("%M")).to_bytes(1, 'big')
        return r

    def add_slider(r, slider_val):
        r += round(slider_val * 63).to_bytes(1, 'big')
        return r

    response = b''
    response += music_obj.is_thing_on('stereo').to_bytes(1, 'big')
    response += music_obj.is_thing_on('bedroom_speakers').to_bytes(1, 'big')
    response += music_obj.is_thing_on('living_room_speakers').to_bytes(1, 'big')
    response += music_obj.spotify_client_on.to_bytes(1, 'big')
    response += music_obj.volume.to_bytes(1, 'big')
    response += music_obj.station.to_bytes(1, 'big')
    response += lights_obj.bedroom_on.to_bytes(1, 'big')
    response += lights_obj.living_room_on.to_bytes(1, 'big')
    response += lights_obj.office_on.to_bytes(1, 'big')
    response += lights_obj.kitchen_on.to_bytes(1, 'big')
    response += lights_obj.ongoing_party.to_bytes(1, 'big')
    response = add_slider(response, lights_obj.brightness)
    response = add_colour(response, lights_obj.rgb_colour)
    response = add_alarm_time(response, alarm_obj.weekday_alarm_time)
    response = add_alarm_time(response, alarm_obj.weekend_alarm_time)

    return response


def run():
    GPIO.setmode(GPIO.BCM)

    mh = music_handler.MusicHandler()
    lh = light_handler.LightHandler()
    rh = router_handler.RouterHandler()

    alarm_watcher = alarm.AlarmWatch(mh, lh)
    alarm_checker = threading.Thread(target=alarm_watcher.alarm_watch)
    alarm_checker.start()

    dead_switch = watcher.PhoneWatch(mh, lh)
    dead_switch_thread = threading.Thread(target=dead_switch.watch)
    dead_switch_thread.start()

    s = socket.socket()
    print("Socket successfully created")
    port = 12345
    s.bind(('', port))
    print("socket bound to %s" % port)
    s.listen(5)
    print("socket is listening")

    # a forever loop until we interrupt it or
    # an error occurs
    while True:
        # Establish connection with client.
        c, address = s.accept()
        print('Got connection from', address)
        command = c.recv(32).strip()
        print(command)

        if command == b'living_room_speakers':
            mh.toggle_living_room()
        elif command == b'bedroom_speakers':
            mh.toggle_bedroom()
        elif command == b'stereo':
            mh.toggle_stereo()
        elif command == b'spotify':
            mh.toggle_spotify()
        elif command == b'kitchen_lights':
            lh.toggle_kitchen_lights()
        elif command == b'office_lights':
            lh.toggle_office_lights()
        elif command == b'living_room_lights':
            lh.toggle_living_room_lights()
        elif command == b'bedroom_lights':
            lh.toggle_bedroom_lights()
        elif command == b'party_mode':
            lh.toggle_party()
        elif command == b'reset_router':
            rh.reset_router()
        elif str(command, 'utf-8').split('#')[0] == 'BRIGHTNESS':
            lh.set_brightness(float((str(command, 'utf-8').split('#')[1])) / 63.0)
        elif str(command, 'utf-8').split('#')[0] == 'COLOUR':
            lh.set_colour(str(command, 'utf-8').split('#')[1])
        elif str(command, 'utf-8').split('#')[0] == 'VOLUME':
            mh.set_volume(int((str(command, 'utf-8').split('#')[1])))
        elif str(command, 'utf-8').split('#')[0] == 'ALARM':
            alarm_watcher.set_alarm(str(command, 'utf-8'))
        elif str(command, 'utf-8').split('#')[0] == 'CLEAR':
            alarm_watcher.clear_alarm(str(command, 'utf-8'))
        elif command in mh.RADIO_STATIONS:
            mh.play_radio(command)
        elif command == b'kill':
            mh.turn_stereo_off()
            lh.kill_all()

        c.send(build_response(mh, lh, alarm_watcher))
        c.close()
