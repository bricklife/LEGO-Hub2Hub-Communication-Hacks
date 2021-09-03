from spike import PrimeHub
from spike.control import wait_for_seconds
import ubluetooth
import ustruct
#import binascii
from micropython import const

hub = PrimeHub()
ble = ubluetooth.BLE()
transmission_id = None

#signal_name_hash = binascii.crc32("ABC".encode())

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
    #if hash == signal_name_hash:
    if value:
        hub.light_matrix.write(value)
    if done:
        hub.light_matrix.show_image('ASLEEP')
        wait_for_seconds(1)
        hub.light_matrix.off()

receive_signal(10 * 1000, _callback)
