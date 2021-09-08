from spike import PrimeHub
import ubluetooth
import ustruct
import utime

crc_table = None

def make_crc_table_if_needed():
    global crc_table
    if crc_table:
        return
    crc_table = [0] * 256
    for i in range(256):
        c = i
        for j in range(8):
            if c & 1:
                c = 0xEDB88320 ^ (c >> 1)
            else:
                c = c >> 1
        crc_table[i] = c

def crc32(buf):
    make_crc_table_if_needed()
    c = 0xFFFFFFFF
    l = len(buf)
    for i in range(l):
        c = crc_table[(c ^ buf[i]) & 0xFF] ^ (c >> 8)
    return c ^ 0xFFFFFFFF

hub = PrimeHub()
ble = ubluetooth.BLE()

count = 0
signal_name_hash = crc32('ABC'.encode())

def transmit_signal(transmission_id, hash, value):
    transmission_id = transmission_id & 0xff
    header = ustruct.pack('<BBBBL', 0xff, 0x03, 0x97, transmission_id, hash)
    data = header + value.encode()[:23]
    
    ble.gap_advertise(100000, adv_data=data, connectable=False)
    utime.sleep_ms(500)
    ble.gap_advertise(None)

while True:
    hub.left_button.wait_until_pressed()
    transmit_signal(count, signal_name_hash, str(count))
    count += 1
