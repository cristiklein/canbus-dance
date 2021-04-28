#!/usr/bin/env python3
import ctypes
import wave
import sys


pa = ctypes.cdll.LoadLibrary('libpulse-simple.so.0')

PA_STREAM_PLAYBACK = 1
PA_STREAM_RECORD = 2
PA_SAMPLE_S16LE = 3
BUFFSIZE = 1024


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


def main(filename):
    """Capture a WAV file with PulseAudio."""

    # Opening a file.
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(44100)

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

    while True:
        # Getting latency.
        latency = pa.pa_simple_get_latency(s, error)
        if latency == -1:
            raise Exception('Getting latency failed!')

        print('{0} usec'.format(latency))

        buf = ctypes.create_string_buffer(BUFFSIZE)
        if pa.pa_simple_read(s, buf, len(buf), error):
            raise Exception('Could not read file!')

        # Reading frames and writing to the stream.
        buf = wf.writeframes(buf)
        if buf == '':
            break


    wf.close()

    # Freeing resources and closing connection.
    pa.pa_simple_free(s)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: ./{0} <filename to record>'.format(sys.argv[0]))
    else:
        main(sys.argv[1])
