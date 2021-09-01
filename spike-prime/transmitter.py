from spike import PrimeHub
import ubluetooth
import ustruct
import utime
#import binascii

hub = PrimeHub()
ble = ubluetooth.BLE()

count = 0
hash = 0xa3830348 # = binascii.crc32("ABC".encode())

def transmit_signal(transmission_id, hash, value):
    transmission_id = transmission_id & 0xff
    header = ustruct.pack('<BBBBL', 0xff, 0x03, 0x97, transmission_id, hash)
    data = header + value.encode()[:23]
    
    ble.gap_advertise(100000, adv_data=data, connectable=False)
    utime.sleep_ms(500)
    ble.gap_advertise(None)

while True:
    hub.left_button.wait_until_pressed()
    transmit_signal(count, hash, str(count))
    count += 1
