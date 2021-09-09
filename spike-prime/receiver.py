from spike import PrimeHub
from spike.control import wait_for_seconds
import ubluetooth
import ustruct
from micropython import const

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
transmission_id = None

signal_name_hash = crc32('ABC'.encode())

_IRQ_SCAN_RESULT    = const(5)
_IRQ_SCAN_DONE      = const(6)

def receive_signal(duration_ms, callback):
    def _bt_irq(event, data):
        global transmission_id
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            if adv_type == 0x02 and len(adv_data) >= 8 and adv_data[:3] == b'\xff\x03\x97':
                tid, hash = ustruct.unpack("<BL", adv_data[3:8])
                if tid != transmission_id:
                    value = adv_data[8:].decode()
                    callback(hash, value, False)
                    transmission_id = tid
        elif event == _IRQ_SCAN_DONE:
            callback(None, None, True)

    ble.active()
    ble.irq(_bt_irq)
    ble.gap_scan(duration_ms, 10000, 10000)

def _callback(hash, value, done):
    if hash == signal_name_hash:
        hub.light_matrix.write(value)
    if done:
        hub.light_matrix.show_image('ASLEEP')
        wait_for_seconds(1)
        hub.light_matrix.off()

receive_signal(10 * 1000, _callback)
