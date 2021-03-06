#!/usr/bin/env python3
import can
import ctypes
import sys

pa = ctypes.cdll.LoadLibrary('libpulse-simple.so.0')

PA_STREAM_PLAYBACK = 1
PA_STREAM_RECORD = 2
PA_SAMPLE_S16LE = 3

#BUF_NSAMPLES = 1024 # ~23ms @ 44.1kHZ
BUF_NSAMPLES = 2048 # ~46ms @ 44.1kHZ

class struct_pa_sample_spec(ctypes.Structure):
    __slots__ = [
        'format',
        'rate',
        'channels',
    ]

struct_pa_sample_spec._fields_ = [
    ('format', ctypes.c_int),
    ('rate', ctypes.c_uint32),
    ('channels', ctypes.c_uint8),
]
pa_sample_spec = struct_pa_sample_spec  # /usr/include/pulse/sample.h:174

def rms(samples):
    return sum([ sample ** 2 for sample in samples ]) / 1024


def main():
    """Capture audio with PulseAudio."""

    # Defining sample format.
    ss = struct_pa_sample_spec()
    ss.rate = 44100
    ss.channels = 1
    ss.format = PA_SAMPLE_S16LE
    error = ctypes.c_int(0)

    # Creating a new record stream.
    s = pa.pa_simple_new(
        None,  # Default server.
        'canbus-dance',  # Application's name.
        PA_STREAM_RECORD,
        None,  # Default device.
        'record',  # Stream's description.
        ctypes.byref(ss),  # Sample format.
        None,  # Default channel map.
        None,  # Default buffering attributes.
        ctypes.byref(error)  # Ignore error code.
    )
    if not s:
        raise Exception('Could not create pulse audio stream: {0}!'.format(
            pa.strerror(ctypes.byref(error))))


    BUF_TYPE = ctypes.c_int16 * BUF_NSAMPLES
    peak = 20000000#0

    bustype = 'socketcan'
    channel = 'vcan0'
    bus = can.interface.Bus(channel=channel, bustype=bustype)

    while True:
        buf = BUF_TYPE()
        if pa.pa_simple_read(s, buf, len(buf), error):
            raise Exception('Could not read buffer!')

        amplitude = rms(buf)
        nstars = min(int(amplitude // (peak / 80)), 80)
        print('*' * nstars + ' ' * (80 - nstars), end = '\r')

        can_ampli = min(int(amplitude // (peak / 0x5F)), 255)
        msg = can.Message(arbitration_id=0x38D,
            data=[can_ampli, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
        bus.send(msg)

    # Freeing resources and closing connection.
    pa.pa_simple_free(s)

if __name__ == '__main__':
    main()
