# DAWN
Server and Android App for controlling IOT boat

This project is comprised of two parts: A server written in Python to be run on a linux device (i.e. a raspberrypi), and an android app.

# Functionalities

- The server controls several relays which are used to provide power to a stereo, 4 speakers, a [NeoPixel](https://learn.adafruit.com/adafruit-neopixel-uberguide) LED strip & a router. Some relays are directly accessible to the end user i.e. stereo & speakers, whereas some are automatic i.e. the LED strip automatically shuts off if no lights are on.
- Music output with the options of:
  - Several internet streams, using [mpc](https://linux.die.net/man/1/mpc) 
  - Spotify using [raspotify](https://github.com/dtcooper/raspotify)
- Lighting, with the options of:
  - Turning on and off sections of the LED strip corresponding to different rooms
  - Adjusting brightness and colour
  - A party mode which delivers a lightshow
- Resetting the router (simply turns off the relay powering it for a few seconds)
- A kill switch - if no device recognised by the server is detected in over half an hour then lights and stereo are switched off
- A welcome home feature - upon a recognised device returning home, if the PIR (passive infrared sensor) detects movement the kitchen lights will turn on

# Installation

This is an incredibly bespoke project, however it should just be a matter of:

- Downloading Dawn_Server to a pi and running the package with Python 3 (I used Python 3.5) (must be as root due to NeoPixel library) i.e. `sudo python3 Dawn_Server`
- Downloading Dawn_App to an android phone and running through e.g. Android Studio

There are however several dependencies. To make it easier to cannibalise my code I've mapped functionalities to dependencies:

| Functionality      | Dependencies |
| -----------        | ----------- |
| Relay Handling | [RPi.GPIO Python package](https://pypi.org/project/RPi.GPIO/) |
| Internet Radio | A configured [mpc](https://linux.die.net/man/1/mpc) playlist |
| Spotify | [raspotify](https://github.com/dtcooper/raspotify) |
| LED Strip Handling | Involves setup depending on configuration - all details can be found over at [adafruit](https://learn.adafruit.com/adafruit-neopixel-uberguide) |
| Colour Selection In App | [ColorPickerPreference](https://github.com/skydoves/ColorPickerPreference) |
| Party Mode | [numpy](https://pypi.org/project/numpy/) for random selection of light show sub-functions |

Feel free to use any part of code, whether to have a raspberrypi controlled music controller, some manner of PIR controlled functionality or some lightshow inspiration.

# Licence

MIT License

Copyright (c) 2021 Andy Parsons

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

