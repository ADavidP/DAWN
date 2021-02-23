import sys
from queue import Queue
from ctypes import POINTER, c_ubyte, c_void_p, c_ulong, cast

# From https://github.com/Valodim/python-pulseaudio
from pulseaudio.lib_pulseaudio import *

# edit to match your sink
SINK_NAME = 'alsa_output.pci-0000_00_1b.0.analog-stereo'
METER_RATE = 344
MAX_SAMPLE_VALUE = 127
DISPLAY_SCALE = 2
MAX_SPACES = MAX_SAMPLE_VALUE >> DISPLAY_SCALE

class PeakMonitor(object):

    def __init__(self, sink_name, rate):
        self.sink_name = sink_name
        self.rate = rate

        # Wrap callback methods in appropriate ctypefunc instances so
        # that the Pulseaudio C API can call them
        self._context_notify_cb = pa_context_notify_cb_t(self.context_notify_cb)
        self._sink_info_cb = pa_sink_info_cb_t(self.sink_info_cb)
        self._stream_read_cb = pa_stream_request_cb_t(self.stream_read_cb)

        # stream_read_cb() puts peak samples into this Queue instance
        self._samples = Queue()

        # Create the mainloop thread and set our context_notify_cb
        # method to be called when there's updates relating to the
        # connection to Pulseaudio
        _mainloop = pa_threaded_mainloop_new()
        _mainloop_api = pa_threaded_mainloop_get_api(_mainloop)
        context = pa_context_new(_mainloop_api, 'peak_demo')
        pa_context_set_state_callback(context, self._context_notify_cb, None)
        pa_context_connect(context, None, 0, None)
        pa_threaded_mainloop_start(_mainloop)

    def __iter__(self):
        while True:
            yield self._samples.get()

    def context_notify_cb(self, context, _):
        state = pa_context_get_state(context)

        if state == PA_CONTEXT_READY:
            print("Pulseaudio connection ready...")
            # Connected to Pulseaudio. Now request that sink_info_cb
            # be called with information about the available sinks.
            o = pa_context_get_sink_info_list(context, self._sink_info_cb, None)
            pa_operation_unref(o)

        elif state == PA_CONTEXT_FAILED :
            print("Connection failed")

        elif state == PA_CONTEXT_TERMINATED:
            print("Connection terminated")

    def sink_info_cb(self, context, sink_info_p, _, __):
        if not sink_info_p:
            return

        sink_info = sink_info_p.contents
        print('-'* 60)
        print('index:', sink_info.index)
        print('name:', sink_info.name)
        print('description:', sink_info.description)

        if sink_info.name == self.sink_name:
            # Found the sink we want to monitor for peak levels.
            # Tell PA to call stream_read_cb with peak samples.
            print('setting up peak recording using', sink_info.monitor_source_name)
            samplespec = pa_sample_spec()
            samplespec.channels = 1
            samplespec.format = PA_SAMPLE_U8
            samplespec.rate = self.rate

            pa_stream = pa_stream_new(context, "peak detect demo", samplespec, None)
            pa_stream_set_read_callback(pa_stream,
                                        self._stream_read_cb,
                                        sink_info.index)
            pa_stream_connect_record(pa_stream,
                                     sink_info.monitor_source_name,
                                     None,
                                     PA_STREAM_PEAK_DETECT)

    def stream_read_cb(self, stream, length, index_incr):
        data = c_void_p()
        pa_stream_peek(stream, data, c_ulong(length))
        data = cast(data, POINTER(c_ubyte))
        for i in xrange(length):
            # When PA_SAMPLE_U8 is used, samples values range from 128
            # to 255 because the underlying audio data is signed but
            # it doesn't make sense to return signed peaks.
            self._samples.put(data[i] - 128)
        pa_stream_drop(stream)

def main():
    monitor = PeakMonitor(SINK_NAME, METER_RATE)
    for sample in monitor:
        sample = sample >> DISPLAY_SCALE
        bar = '>' * sample
        spaces = ' ' * (MAX_SPACES - sample)
        print(' %3d %s%s\r' % (sample, bar, spaces),)
        sys.stdout.flush()

if __name__ == '__main__':
    main()


# #!/usr/bin/env python
#
# # 8 bar Audio equaliser using MCP2307
#
# import alsaaudio as aa
# from time import sleep
# from struct import unpack
# import numpy as np
#
# # Set up audio
# sample_rate = 44100
# no_channels = 2
# chunk = 512  # Use a multiple of 8
#
# print(aa.pcms(aa.PCM_CAPTURE))
#
# data_in = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL)
# data_in.setchannels(no_channels)
# data_in.setrate(sample_rate)
# data_in.setformat(aa.PCM_FORMAT_S16_LE)
# data_in.setperiodsize(chunk)
#
#
# def calculate_levels(data, chunk):
#     # Convert raw data to numpy array
#     data = unpack("%dh" % (len(data) / 2), data)
#     data = np.array(data, dtype='h')
#     # Apply FFT - real data so rfft used
#     fourier = np.fft.rfft(data)
#     # Remove last element in array to make it the same size as chunk
#     fourier = np.delete(fourier, len(fourier) - 1)
#     # Find amplitude
#     power = np.log10(np.abs(fourier)) ** 2
#     # Araange array into 8 rows for the 8 bars on LED matrix
#     power = np.reshape(power, (8, chunk / 8))
#     matrix = np.int_(np.average(power, axis=1) / 4)
#     print(matrix)
#     return matrix
#
#
# print("Processing.....")
#
# while True:
#     # Read data from device
#     l, data = data_in.read()
#     data_in.pause(1)  # Pause capture whilst RPi processes data
#     if l:
#         try:
#             matrix = calculate_levels(data, chunk)
#             # for i in range(0, 8):
#             #     Set_Column((1 << matrix[i]) - 1, 0xFF ^ (1 << i))
#         except Exception as e:
#             print(e)
#
#     sleep(0.001)
#     data_in.pause(0)  # Resume capture
