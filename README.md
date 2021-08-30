# LEGO MINDSTORMS Robot Inventor's Hub to Hub Communication Hacks

LEGO MINDSTORMS Robot Inventor's Hub to Hub Communication is implemented on Bluetooth LE (BLE) Advertising.

For example, when a hub transmits a signal "ABC" with a value "123", some **INVALID** advertising packets will be sent as follows:

<img src="Images/transmit-block.png">
<img src="Images/advertising-packet.png">

## Data structure

`FF 03 97 01 48 03 83 A3 31 32 33`

| Bytes | Meaning |
| --- | --- |
| `FF 03 97` | Fixed header |
| `01` | Signal ID |
| `48 03 83 A3` | Signal name hash = CRC32("ABC") = 0xA3830348 |
| `31 32 33` | Value = "123"  |

## Transmit signal by hcitool

```
$ hcitool -i hci0 cmd 0x08 0x0006 a0 00 a0 00 02 00 00 00 00 00 00 00 00 07 00
$ hcitool -i hci0 cmd 0x08 0x0008 0b ff 03 97 01 48 03 83 a3 31 32 33
$ hcitool -i hci0 cmd 0x08 0x000a 01
```

## Demo
- Transmit signals from Raspberry Pi Zero W https://www.youtube.com/watch?v=K0kwiPHDSnw
  - Python 3.x scrpit: [rpi-counter.py](python3-scripts/rpi-counter.py) using [hub2hub.py](python3-scripts/hub2hub.py)

