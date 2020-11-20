import threading
import time
import board
import neopixel
import RPi.GPIO as GPIO

BEDROOM_LIGHTS_RELAY = 18
LIVING_ROOM_LIGHTS_RELAY = 15


class LightHandler:

    PORT_CABIN_LEDS = 73
    STERN_LEDS = 27
    STARBOARD_CABIN_LEDS = 83
    STARBOARD_BR_LEDS = 37
    BOW_LEDS = 27
    PORT_BR_LEDS = 36

    # Choose an open pin connected to the Data In of the NeoPixel strip.
    PIXEL_PIN = board.D21
    NUM_PIXELS = STARBOARD_CABIN_LEDS + STERN_LEDS + PORT_CABIN_LEDS + STARBOARD_BR_LEDS + BOW_LEDS + PORT_BR_LEDS

    # The order of the pixel colors - although actual order is BGR.
    ORDER = neopixel.RGB

    START_LIVING_ROOM_PORT_LED = 0
    END_LIVING_ROOM_PORT_LED = PORT_CABIN_LEDS - 34
    START_LIVING_ROOM_STARBOARD_LED = 35 + PORT_CABIN_LEDS + STERN_LEDS
    END_LIVING_ROOM_STARBOARD_LED = START_LIVING_ROOM_STARBOARD_LED + END_LIVING_ROOM_PORT_LED

    START_OFFICE_LED = 10
    END_OFFICE_LED = 26

    START_KITCHEN_PORT_LED = END_LIVING_ROOM_PORT_LED
    END_KITCHEN_PORT_LED = PORT_CABIN_LEDS
    START_KITCHEN_STARBOARD_LED = END_KITCHEN_PORT_LED + STERN_LEDS
    END_KITCHEN_STARBOARD_LED = START_LIVING_ROOM_STARBOARD_LED

    START_BEDROOM_STARBOARD_LED = PORT_CABIN_LEDS + STERN_LEDS + STARBOARD_CABIN_LEDS
    END_BEDROOM_STARBOARD_LED = START_BEDROOM_STARBOARD_LED + STARBOARD_BR_LEDS
    START_BEDROOM_PORT_LED = END_BEDROOM_STARBOARD_LED + BOW_LEDS
    END_BEDROOM_PORT_LED = NUM_PIXELS

    def __init__(self):
        self.relays_on = False
        self.setup_gpio()
        self.pixels = neopixel.NeoPixel(self.PIXEL_PIN,
                                        self.NUM_PIXELS,
                                        brightness=12 / 14.5,  # Allows for voltage drop,
                                        auto_write=False,
                                        pixel_order=self.ORDER)
        self.br_on = False
        self.lr_on = False
        self.k_on = False
        self.o_on = False
        self.brightness = 1
        self.ongoing_party = False

        self.party_time = None

    @staticmethod
    def setup_gpio():
        GPIO.setup(BEDROOM_LIGHTS_RELAY, GPIO.OUT, initial=True)
        GPIO.setup(LIVING_ROOM_LIGHTS_RELAY, GPIO.OUT, initial=True)

    def enable_lights_relay(self):
        GPIO.output(BEDROOM_LIGHTS_RELAY, False)
        GPIO.output(LIVING_ROOM_LIGHTS_RELAY, False)
        self.relays_on = True

    def disable_lights_relay(self):
        GPIO.output(BEDROOM_LIGHTS_RELAY, True)
        GPIO.output(LIVING_ROOM_LIGHTS_RELAY, True)
        self.relays_on = False

    def scale_light(self, t, scale):
        if not 0 <= scale <= 1:
            scale = 1
        return tuple(int(c * scale) for c in reversed(t))

    def set_batch(self, start, end, brightness=1):
        self.ongoing_party = False
        if self.party_time is not None:
            while self.party_time.isAlive():
                time.sleep(0.001)
        for i in range(start, end):
            self.pixels[i] = self.scale_light((255, 255, 41), brightness)
        if all([pixel == (0, 0, 0) for pixel in self.pixels]):
            self.disable_lights_relay()
        else:
            self.enable_lights_relay()
            time.sleep(0.002)
        self.pixels.show()

    def toggle_living_room_lights(self):
        if self.lr_on:
            self.set_batch(self.START_LIVING_ROOM_PORT_LED, self.END_LIVING_ROOM_PORT_LED, brightness=0)
            self.set_batch(self.START_LIVING_ROOM_STARBOARD_LED, self.END_LIVING_ROOM_STARBOARD_LED, brightness=0)
            self.lr_on = False
            self.o_on = False
        else:
            self.set_batch(self.START_LIVING_ROOM_PORT_LED, self.END_LIVING_ROOM_PORT_LED, self.brightness)
            self.set_batch(self.START_LIVING_ROOM_STARBOARD_LED, self.END_LIVING_ROOM_STARBOARD_LED, self.brightness)
            self.lr_on = True
            self.o_on = True

    def toggle_office_lights(self):
        if not self.lr_on:
            if self.o_on:
                self.set_batch(self.START_OFFICE_LED, self.END_OFFICE_LED, brightness=0)
                self.o_on = False
            else:
                self.set_batch(self.START_OFFICE_LED, self.END_OFFICE_LED, self.brightness)
                self.o_on = True

    def toggle_kitchen_lights(self):
        if self.k_on:
            self.set_batch(self.START_KITCHEN_PORT_LED, self.END_KITCHEN_PORT_LED, brightness=0)
            self.set_batch(self.START_KITCHEN_STARBOARD_LED, self.END_KITCHEN_STARBOARD_LED, brightness=0)
            self.k_on = False
        else:
            self.set_batch(self.START_KITCHEN_PORT_LED, self.END_KITCHEN_PORT_LED, self.brightness)
            self.set_batch(self.START_KITCHEN_STARBOARD_LED, self.END_KITCHEN_STARBOARD_LED, self.brightness)
            self.k_on = True

    def toggle_bedroom_lights(self):
        if self.br_on:
            self.set_batch(self.START_BEDROOM_PORT_LED, self.END_BEDROOM_PORT_LED, brightness=0)
            self.set_batch(self.START_BEDROOM_STARBOARD_LED, self.END_BEDROOM_STARBOARD_LED, brightness=0)
            self.br_on = False
        else:
            self.set_batch(self.START_BEDROOM_PORT_LED, self.END_BEDROOM_PORT_LED, self.brightness)
            self.set_batch(self.START_BEDROOM_STARBOARD_LED, self.END_BEDROOM_STARBOARD_LED, self.brightness)
            self.br_on = True

    def set_brightness(self, brightness):
        self.brightness = brightness
        if self.lr_on:
            self.set_batch(self.START_LIVING_ROOM_PORT_LED, self.END_LIVING_ROOM_PORT_LED, self.brightness)
            self.set_batch(self.START_LIVING_ROOM_STARBOARD_LED, self.END_LIVING_ROOM_STARBOARD_LED, self.brightness)
        if self.o_on:
            self.set_batch(self.START_OFFICE_LED, self.END_OFFICE_LED, self.brightness)
        if self.k_on:
            self.set_batch(self.START_KITCHEN_PORT_LED, self.END_KITCHEN_PORT_LED, self.brightness)
            self.set_batch(self.START_KITCHEN_STARBOARD_LED, self.END_KITCHEN_STARBOARD_LED, self.brightness)
        if self.br_on:
            self.set_batch(self.START_BEDROOM_PORT_LED, self.END_BEDROOM_PORT_LED, self.brightness)
            self.set_batch(self.START_BEDROOM_STARBOARD_LED, self.END_BEDROOM_STARBOARD_LED, self.brightness)

    def toggle_party(self):
        if self.ongoing_party:
            self.kill_all()
        else:
            self.ongoing_party = True
            self.party_time = threading.Thread(target=self.party_mode)
            self.party_time.start()

    def kill_all(self):
        self.set_batch(0, self.NUM_PIXELS, brightness=0)
        self.br_on = False
        self.lr_on = False
        self.k_on = False

    def party_mode(self):
        def rainbow_cycle():
            def wheel(pos):
                # Input a value 0 to 255 to get a color value.
                # The colours are a transition r - g - b - back to r.
                if pos < 0 or pos > 255:
                    r = g = b = 0
                elif pos < 85:
                    r = int(pos * 3)
                    g = int(255 - pos * 3)
                    b = 0
                elif pos < 170:
                    pos -= 85
                    r = int(255 - pos * 3)
                    g = 0
                    b = int(pos * 3)
                else:
                    pos -= 170
                    r = 0
                    g = int(pos * 3)
                    b = int(255 - pos * 3)
                return r, g, b

            while True:
                for j in range(255):
                    for i in range(self.NUM_PIXELS):
                        pixel_index = (i * 256 // self.NUM_PIXELS) + j
                        self.pixels[i] = wheel(pixel_index & 255)
                    self.pixels.show()
                    time.sleep(0.001)
                    if not self.ongoing_party:
                        return

        for i in range(0, self.NUM_PIXELS):
            self.pixels[i] = (0, 0, 0)
        self.br_on = False
        self.lr_on = False
        self.k_on = False
        if not self.relays_on:
            self.enable_lights_relay()
            time.sleep(0.002)

        rainbow_cycle()

        for i in range(0, self.NUM_PIXELS):
            self.pixels[i] = (0, 0, 0)
