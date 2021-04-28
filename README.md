CAN-BUS Dance
=============
This project is about using the RPM and speed meter on a PSA car (e.g., Peugeot 307) as a VU meter.

As the licence puts it, this project is definitely not fit for any purpose. Those who judge a project by its utility can stop reading now.

Architecture
------------

```
Spotify --(pulseaudio)--> canbus-dance --(SocketCAN)--> USB2CAN --(OBD2)--> Car's dashboard
```

DONE
----
* Figure out how to control RPM and speed meter on car's dashboard.
* Capture PulseAudio sound.

TODO
----
* Do RMS.
* Convert RMS into SocketCAN message.
