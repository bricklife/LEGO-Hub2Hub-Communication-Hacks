# LEGO MINDSTORMS Robot Inventor's Hub to Hub Communication Hacks

LEGO MINDSTORMS Robot Inventor's Hub to Hub Communication is implemented on Bluetooth LE (BLE) Advertising. For example, when a hub transmits a signal "ABC" with a value "123", some **INVALID** advertising packets will be sent as follows:

<img src="Images/transmit-block.png">
<img src="Images/advertising-packet.png">

## Data Structure

`FF 03 97 01 48 03 83 A3 31 32 33`

| Bytes | Meaning |
| --- | --- |
| `FF 03 97` | Fixed header |
| `01` | Signal ID |
| `48 03 83 A3` | Signal Hash = CRC32("ABC") = 0xA3830348 |
| `31 32 33` | Value = "123"  |


## Demo
Transmit signals from Raspberry Pi Zero W
https://www.youtube.com/watch?v=K0kwiPHDSnw

