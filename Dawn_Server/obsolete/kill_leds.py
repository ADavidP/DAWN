import time
import board
import neopixel


# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D21

PORT_LR_LEDS = 73
STERN_LEDS = 27
STARBOARD_LR_LEDS = 83
STARBOARD_BR_LEDS = 37
BOW_LEDS = 27
PORT_BR_LEDS = 36

# The number of NeoPixels
num_pixels = PORT_LR_LEDS + STERN_LEDS + STARBOARD_LR_LEDS + STARBOARD_BR_LEDS + BOW_LEDS + PORT_BR_LEDS

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False,
                           pixel_order=ORDER)
pixels.fill((0, 0, 0))
pixels.show()
