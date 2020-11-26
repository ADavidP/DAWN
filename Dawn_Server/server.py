import threading

import socket
import music_handler
import warm_glow
import alarm
import watcher
import RPi.GPIO as GPIO


def build_response(music_obj, lights_obj, alarm_obj):
    """Builds response to any message from app"""

    def add_alarm_time(r, alarm_time):
        """Adds alarm time to response"""
        if alarm_time is None:
            r += False.to_bytes(2, 'big')
            r += (0).to_bytes(4, 'big')
        else:
            r += True.to_bytes(2, 'big')
            r += int(alarm_time.strftime("%H")).to_bytes(2, 'big')
            r += int(alarm_time.strftime("%M")).to_bytes(2, 'big')
        return r

    def add_slider(r, slider_val):
        r += round(slider_val * 63).to_bytes(2, 'big')
        return r

    response = b''
    response += music_obj.is_thing_on('radio').to_bytes(2, 'big')
    response += music_obj.is_thing_on('bedroom').to_bytes(2, 'big')
    response += music_obj.is_thing_on('living').to_bytes(2, 'big')
    response += music_obj.spotify_client_on.to_bytes(2, 'big')
    response += music_obj.radio_client_on.to_bytes(2, 'big')
    response += music_obj.volume.to_bytes(2, 'big')
    response += music_obj.station.to_bytes(2, 'big')
    response += lights_obj.br_on.to_bytes(2, 'big')
    response += lights_obj.lr_on.to_bytes(2, 'big')
    response += lights_obj.o_on.to_bytes(2, 'big')
    response += lights_obj.k_on.to_bytes(2, 'big')
    response += lights_obj.ongoing_party.to_bytes(2, 'big')
    response = add_slider(response, lights_obj.brightness)
    response = add_alarm_time(response, alarm_obj.weekday_alarm_time)
    response = add_alarm_time(response, alarm_obj.weekend_alarm_time)

    return response


def run():
    GPIO.setmode(GPIO.BCM)

    mh = music_handler.MusicHandler()
    lh = warm_glow.LightHandler()

    alarm_watcher = alarm.AlarmWatch(mh, lh)
    alarm_checker = threading.Thread(target=alarm_watcher.alarm_watch)
    alarm_checker.start()

    dead_switch = watcher.PhoneWatch(mh, lh)
    dead_switch_thread = threading.Thread(target=dead_switch.watch)
    dead_switch_thread.start()

    # next create a socket object
    s = socket.socket()
    print("Socket successfully created")
    port = 12345

    s.bind(('', port))
    print("socket binded to %s" % (port))

    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")

    # a forever loop until we interrupt it or
    # an error occurs
    while True:
        # Establish connection with client.
        c, addr = s.accept()
        print('Got connection from', addr)
        command = c.recv(32).strip()
        print(command)

        if command == b'living_room':
            mh.toggle_livingroom()
        elif command == b'bed_room':
            mh.toggle_bedroom()
        elif command == b'radio':
            mh.toggle_radio()
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
        elif str(command, 'utf-8').split('#')[0] == 'BRIGHTNESS':
            lh.set_brightness(float((str(command, 'utf-8').split('#')[1]))/63.0)
        elif str(command, 'utf-8').split('#')[0] == 'VOLUME':
            mh.set_volume(int((str(command, 'utf-8').split('#')[1])))
        elif str(command, 'utf-8').split('#')[0] == 'ALARM':
            alarm_watcher.set_alarm(str(command, 'utf-8'))
        elif str(command, 'utf-8').split('#')[0] == 'CLEAR':
            alarm_watcher.clear_alarm(str(command, 'utf-8'))
        elif command in mh.radio_stations:
            mh.play_radio(command)
        elif command == b'kill':
            mh.turn_radio_off()
            lh.kill_all()

        # Send response
        c.send(build_response(mh, lh, alarm_watcher))

        # Close the connection with the client
        c.close()


run()
