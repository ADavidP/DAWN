"""Module for handling control of lighting strip.
Lights are controlled in batches. If no batches are on then the two relays which control power to the strip are
switched off (as the strip still draws power even when all lights are off). Functionality also exists for a party
mode whereby random functions of light shows are chosen from a weighted list.
A note about architecture: LED pixels will be turned on by a single Python process which can then go and do something
else, but to constantly update pixels i.e. party mode, requires a process to be constantly engaged so is therefore
handled by a separate thread which regularly checks for interrupts.
"""
import threading
import time
import random

from numpy.random import choice
import board
import neopixel
import RPi.GPIO as GPIO

BEDROOM_LIGHTS_RELAY = 18
LIVING_ROOM_LIGHTS_RELAY = 15


def rgb_to_brg(rgb_colour):
    """Reorders RGB colour value to that used by DAWN's LED strip"""
    return (
        rgb_colour[2],
        rgb_colour[0],
        rgb_colour[1]
    )


def brg_to_rgb(brg_colour):
    """Reorders RGB colour value used by DAWN's LED strip to standard RGB order"""
    return (
        brg_colour[1],
        brg_colour[2],
        brg_colour[0]
    )


class LightHandler:
    """Overarching class for handling lighting"""
    
    # Number of LED addresses in each part of the boat
    PORT_CABIN_LEDS = 73
    STERN_LEDS = 27
    STARBOARD_CABIN_LEDS = 83
    STARBOARD_BR_LEDS = 37
    BOW_LEDS = 27
    PORT_BR_LEDS = 36
    NUM_PIXELS = (STARBOARD_CABIN_LEDS + STERN_LEDS + PORT_CABIN_LEDS +
                  STARBOARD_BR_LEDS + BOW_LEDS + PORT_BR_LEDS)  # Total of 383
    
    # Derived starts and ends of subsections of strip used for lighting
    START_LIVING_ROOM_PORT_LED = 0
    END_LIVING_ROOM_PORT_LED = 39
    START_OFFICE_LED = 10
    END_OFFICE_LED = 26
    START_KITCHEN_PORT_LED = END_LIVING_ROOM_PORT_LED
    END_KITCHEN_PORT_LED = PORT_CABIN_LEDS
    START_KITCHEN_STARBOARD_LED = END_KITCHEN_PORT_LED + STERN_LEDS
    END_KITCHEN_STARBOARD_LED = START_KITCHEN_STARBOARD_LED + 35
    START_LIVING_ROOM_STARBOARD_LED = END_KITCHEN_STARBOARD_LED
    END_LIVING_ROOM_STARBOARD_LED = START_LIVING_ROOM_STARBOARD_LED + END_LIVING_ROOM_PORT_LED
    START_BEDROOM_STARBOARD_LED = PORT_CABIN_LEDS + STERN_LEDS + STARBOARD_CABIN_LEDS
    END_BEDROOM_STARBOARD_LED = START_BEDROOM_STARBOARD_LED + STARBOARD_BR_LEDS
    START_BEDROOM_PORT_LED = END_BEDROOM_STARBOARD_LED + BOW_LEDS
    END_BEDROOM_PORT_LED = NUM_PIXELS

    # Pin which LED strip is connected to
    PIXEL_PIN = board.D21

    # The order of the pixel colors - although actual order is BRG.
    ORDER = neopixel.RGB

    # Preset Colours
    DEFAULT = rgb_to_brg((255, 255, 41))

    RED = rgb_to_brg((255, 0, 0))
    PURPLE = rgb_to_brg((255, 0, 255))
    BLUE = rgb_to_brg((0, 0, 255))
    GREEN = rgb_to_brg((0, 255, 0))
    YELLOW = rgb_to_brg((255, 255, 0))
    ORANGE = rgb_to_brg((255, 165, 0))

    PRESET_COLOURS = (RED, PURPLE, BLUE, GREEN, YELLOW, ORANGE)
    REVERSED_COLOURS = tuple(reversed(PRESET_COLOURS))

    # Lower brightness value changes are more perceivable. Interpolated modified sin function used
    # to get slower 'glow up' used in certain party functions
    GLOW_SCALE = [0, 0, 1, 1, 2, 3, 5, 6, 8, 10, 12, 15, 18, 21, 24, 27, 31, 35, 39, 43, 47, 52, 57, 62, 67, 72, 78, 84,
                  90, 96, 102, 108, 115, 121, 128, 135, 142, 149, 156, 163, 171, 178, 185, 193, 201, 208, 216, 224, 232,
                  239, 247, 255]

    def __init__(self):
        self.relays_on = False
        self.setup_gpio()
        # LED strip is only rated for a voltage of up to 12V. DAWN's voltage goes up to 14.5, so brightness is scaled
        # down in order to reduce the risk of damage.
        self.pixels = neopixel.NeoPixel(self.PIXEL_PIN,
                                        self.NUM_PIXELS,
                                        brightness=12/14.5,
                                        auto_write=False,
                                        pixel_order=self.ORDER)
        self.bedroom_on = False
        self.living_room_on = False
        self.kitchen_on = False
        self.office_on = False
        
        self.brightness = 1
        
        self.rgb_colour = brg_to_rgb(self.DEFAULT)
        self.colour = self.DEFAULT
        
        self.ongoing_party = False
        self.party_time = None
        self.previous_party_colour = None

    @staticmethod
    def setup_gpio():
        """Sets up relays"""
        GPIO.setup(BEDROOM_LIGHTS_RELAY, GPIO.OUT, initial=True)
        GPIO.setup(LIVING_ROOM_LIGHTS_RELAY, GPIO.OUT, initial=True)

    def enable_lights_relay(self):
        """Closes relays"""
        GPIO.output(BEDROOM_LIGHTS_RELAY, False)
        GPIO.output(LIVING_ROOM_LIGHTS_RELAY, False)
        self.relays_on = True

    def disable_lights_relay(self):
        """Opens relays"""
        GPIO.output(BEDROOM_LIGHTS_RELAY, True)
        GPIO.output(LIVING_ROOM_LIGHTS_RELAY, True)
        self.relays_on = False

    def set_batch(self, start, end, brightness=1):
        """Sets a batch of LEDs to a certain brightness"""

        def scale_light(colour, scale):
            """Scales colour to brightness level"""
            if not 0 <= scale <= 1:
                scale = 1
            return tuple(int(pigment * scale) for pigment in colour)

        # If turning on normal lights, want to stop party mode
        self.ongoing_party = False
        if self.party_time is not None:
            while self.party_time.isAlive():
                time.sleep(0.001)

        for i in range(start, end):
            self.pixels[i] = scale_light(self.colour, brightness)
        if all([pixel == (0, 0, 0) for pixel in self.pixels]):
            self.disable_lights_relay()
        else:
            self.enable_lights_relay()
            # Let physical relay engage
            time.sleep(0.002)
        self.pixels.show()

    def toggle_living_room_lights(self):
        # Note that office lights are a subset of living room lights
        if self.living_room_on:
            self.set_batch(self.START_LIVING_ROOM_PORT_LED, self.END_LIVING_ROOM_PORT_LED, brightness=0)
            self.set_batch(self.START_LIVING_ROOM_STARBOARD_LED, self.END_LIVING_ROOM_STARBOARD_LED, brightness=0)
            self.living_room_on = False
            self.office_on = False
        else:
            self.set_batch(self.START_LIVING_ROOM_PORT_LED, self.END_LIVING_ROOM_PORT_LED, self.brightness)
            self.set_batch(self.START_LIVING_ROOM_STARBOARD_LED, self.END_LIVING_ROOM_STARBOARD_LED, self.brightness)
            self.living_room_on = True
            self.office_on = True

    def toggle_office_lights(self):
        # Note that office lights are a subset of living room lights
        if not self.living_room_on:
            if self.office_on:
                self.set_batch(self.START_OFFICE_LED, self.END_OFFICE_LED, brightness=0)
                self.office_on = False
            else:
                self.set_batch(self.START_OFFICE_LED, self.END_OFFICE_LED, self.brightness)
                self.office_on = True

    def toggle_kitchen_lights(self):
        if self.kitchen_on:
            self.set_batch(self.START_KITCHEN_PORT_LED, self.END_KITCHEN_PORT_LED, brightness=0)
            self.set_batch(self.START_KITCHEN_STARBOARD_LED, self.END_KITCHEN_STARBOARD_LED, brightness=0)
            self.kitchen_on = False
        else:
            self.set_batch(self.START_KITCHEN_PORT_LED, self.END_KITCHEN_PORT_LED, self.brightness)
            self.set_batch(self.START_KITCHEN_STARBOARD_LED, self.END_KITCHEN_STARBOARD_LED, self.brightness)
            self.kitchen_on = True

    def toggle_bedroom_lights(self):
        if self.bedroom_on:
            self.set_batch(self.START_BEDROOM_PORT_LED, self.END_BEDROOM_PORT_LED, brightness=0)
            self.set_batch(self.START_BEDROOM_STARBOARD_LED, self.END_BEDROOM_STARBOARD_LED, brightness=0)
            self.bedroom_on = False
        else:
            self.set_batch(self.START_BEDROOM_PORT_LED, self.END_BEDROOM_PORT_LED, self.brightness)
            self.set_batch(self.START_BEDROOM_STARBOARD_LED, self.END_BEDROOM_STARBOARD_LED, self.brightness)
            self.bedroom_on = True

    def set_brightness(self, brightness):
        self.brightness = brightness
        self.refresh_lights()

    def set_colour(self, colour):
        # Convert colour from string to list
        self.rgb_colour = []
        for i in range(0, len(colour), 2):
            self.rgb_colour.append(int(colour[i:i+2], 16))
        self.colour = rgb_to_brg(self.rgb_colour)
        self.refresh_lights()

    def refresh_lights(self):
        if self.living_room_on:
            self.set_batch(self.START_LIVING_ROOM_PORT_LED, self.END_LIVING_ROOM_PORT_LED, self.brightness)
            self.set_batch(self.START_LIVING_ROOM_STARBOARD_LED, self.END_LIVING_ROOM_STARBOARD_LED, self.brightness)
        if self.office_on:
            self.set_batch(self.START_OFFICE_LED, self.END_OFFICE_LED, self.brightness)
        if self.kitchen_on:
            self.set_batch(self.START_KITCHEN_PORT_LED, self.END_KITCHEN_PORT_LED, self.brightness)
            self.set_batch(self.START_KITCHEN_STARBOARD_LED, self.END_KITCHEN_STARBOARD_LED, self.brightness)
        if self.bedroom_on:
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
        self.bedroom_on = False
        self.living_room_on = False
        self.office_on = False
        self.kitchen_on = False

    def party_mode(self):
        """Gives light display by selecting sub-light shows from weighted list at random"""

        def wheel(pos):
            """Input a value 0 to 255 to get a color value. The colours are a transition r - g - b - back to r.
            Credit: Adafruit NeoPixel example
            """
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
            return rgb_to_brg((r, g, b))

        def rainbow_chase():
            for i in range(255):
                for j in range(self.NUM_PIXELS):
                    if i % 3 == j % 3:
                        self.pixels[j] = wheel(i)
                    else:
                        self.pixels[j] = (0, 0, 0)
                self.pixels.show()
                for k in range(50):
                    time.sleep(0.001)
                    if not self.ongoing_party:
                        return
            for i in range(0, self.NUM_PIXELS):
                self.pixels[i] = (0, 0, 0)
            self.pixels.show()

        def subdued_rainbow_chase():
            colours = random.choice([self.PRESET_COLOURS, self.REVERSED_COLOURS])
            for i in range(50):
                for j in range(self.NUM_PIXELS):
                    if i % 10 == j % 10:
                        self.pixels[j] = tuple((round(0.5 * pigment) for pigment in colours[i % len(colours)]))
                    else:
                        self.pixels[j] = (0, 0, 0)
                self.pixels.show()
                for k in range(75):
                    time.sleep(0.01)
                    if not self.ongoing_party:
                        return
            for i in range(0, self.NUM_PIXELS):
                self.pixels[i] = (0, 0, 0)
            self.pixels.show()

        def rainbow_chase_reverse():
            for i in range(255):
                for j in range(self.NUM_PIXELS):
                    if (3 - i) % 3 == j % 3:
                        self.pixels[j] = wheel(i)
                    else:
                        self.pixels[j] = (0, 0, 0)
                self.pixels.show()
                for k in range(50):
                    time.sleep(0.001)
                    if not self.ongoing_party:
                        return
            for i in range(0, self.NUM_PIXELS):
                self.pixels[i] = (0, 0, 0)
            self.pixels.show()

        def subdued_rainbow_chase_reverse():
            colours = random.choice([self.PRESET_COLOURS, self.REVERSED_COLOURS])
            for i in range(50):
                for j in range(self.NUM_PIXELS):
                    if (10 - i) % 10 == j % 10:
                        self.pixels[j] = tuple((round(0.5 * pigment) for pigment in colours[i % len(colours)]))
                    else:
                        self.pixels[j] = (0, 0, 0)
                self.pixels.show()
                for k in range(75):
                    time.sleep(0.01)
                    if not self.ongoing_party:
                        return
            for i in range(0, self.NUM_PIXELS):
                self.pixels[i] = (0, 0, 0)
            self.pixels.show()

        def rainbow_cycle():
            """Credit: Adafruit NeoPixel example"""
            for k in range(4):
                for i in range(255):
                    for j in range(self.NUM_PIXELS):
                        pixel_index = i + (j * 256 // self.NUM_PIXELS)
                        self.pixels[j] = wheel(pixel_index & 255)
                    self.pixels.show()
                    time.sleep(0.001)
                    if not self.ongoing_party:
                        return
            for i in range(0, self.NUM_PIXELS):
                self.pixels[i] = (0, 0, 0)
            self.pixels.show()

        def new_random_colour():
            colour = random.choice(self.PRESET_COLOURS)
            while colour == self.previous_party_colour:
                colour = random.choice(self.PRESET_COLOURS)
            self.previous_party_colour = colour
            return colour

        def subdued_glow():
            colour = new_random_colour()
            pixels_to_show = []
            for i in range(random.randint(0, 12), self.NUM_PIXELS, 15):
                cluster_end = i + 3 if i + 3 <= self.NUM_PIXELS else self.NUM_PIXELS
                for j in range(i, cluster_end):
                    pixels_to_show.append(j)

            for i in self.GLOW_SCALE:
                pixel_setting = tuple((round((i / 255) * pigment) for pigment in colour))
                for pixel in pixels_to_show:
                    self.pixels[pixel] = pixel_setting
                self.pixels.show()
                time.sleep(0.1)
                if not self.ongoing_party:
                    return
            for i in reversed(self.GLOW_SCALE):
                pixel_setting = tuple((round((i / 255) * pigment) for pigment in colour))
                for pixel in pixels_to_show:
                    self.pixels[pixel] = pixel_setting
                self.pixels.show()
                time.sleep(0.1)
                if not self.ongoing_party:
                    return

        def burst(sleep_time):
            if sleep_time < 0.1:
                repeats = 5
            else:
                repeats = 1
            for r in range(repeats):
                colour = new_random_colour()
                for _ in range(5):
                    rand_ints = [random.randint(self.START_BEDROOM_STARBOARD_LED + 13, self.NUM_PIXELS - 13)]
                    first_lr_seed = random.randint(13, self.END_LIVING_ROOM_STARBOARD_LED - 13)
                    rand_ints.append(first_lr_seed)
                    second_lr_seed = random.randint(13, self.END_LIVING_ROOM_STARBOARD_LED - 13)
                    while first_lr_seed - 13 < second_lr_seed < first_lr_seed + 13:
                        second_lr_seed = random.randint(13, self.END_LIVING_ROOM_STARBOARD_LED - 13)
                    rand_ints.append(second_lr_seed)
                    for i in range(0, len(self.GLOW_SCALE) + 13):
                        for seed_pixel in rand_ints:
                            affected_pixels = range(seed_pixel - 13, seed_pixel + 13)
                            for j in affected_pixels:
                                distance_from_seed = abs(j - seed_pixel)
                                if 0 <= i - distance_from_seed < len(self.GLOW_SCALE) - 1:
                                    self.pixels[j % self.NUM_PIXELS] = (
                                        tuple((round((self.GLOW_SCALE[i - distance_from_seed] / 255) * pigment)
                                               for pigment in colour))
                                    )
                                else:
                                    self.pixels[j % self.NUM_PIXELS] = (0, 0, 0)
                        self.pixels.show()
                        time.sleep(sleep_time)
                        if not self.ongoing_party:
                            return

        def quick_burst():
            return burst(0.001)

        def slow_burst():
            return burst(0.15)

        def strobe():
            for i in range(180):
                for j in range(self.NUM_PIXELS):
                    self.pixels[j] = (255, 255, 255)
                    if not self.ongoing_party:
                        return
                self.pixels.show()
                time.sleep(0.001)
                for j in range(self.NUM_PIXELS):
                    self.pixels[j] = (0, 0, 0)
                    if not self.ongoing_party:
                        return
                self.pixels.show()
                time.sleep(0.003)

        for pixel_i in range(0, self.NUM_PIXELS):
            self.pixels[pixel_i] = (0, 0, 0)
        self.bedroom_on = False
        self.living_room_on = False
        self.office_on = False
        self.kitchen_on = False
        if not self.relays_on:
            self.enable_lights_relay()
            # Let physical relay engage
            time.sleep(0.002)

        party_directives = [subdued_glow, slow_burst, subdued_rainbow_chase, subdued_rainbow_chase_reverse, quick_burst,
                            rainbow_chase, rainbow_chase_reverse, rainbow_cycle, strobe]
        weights = [0.32, 0.32, 0.075, 0.075, 0.185, 0.0025, 0.0025, 0.019, 0.001]

        while self.ongoing_party:
            choice(party_directives, p=weights)()

        # This code reached when party stops
        for pixel_i in range(0, self.NUM_PIXELS):
            self.pixels[pixel_i] = (0, 0, 0)
