import bluetooth._bluetooth as bluez
import binascii
import struct
import time

def _set_advertising_parameters(sock, interval):
    interval = interval & 0xffff
    type = 0x02 # ADV_SCAN_IND
    param = struct.pack('<HHBBB6sBB', interval, interval, type, 0, 0, b'', 7, 0)
    bluez.hci_send_cmd(sock, 0x08, 0x0006, param)

def _set_advertising_data(sock, data):
    data = data[:31]
    param = bytes([len(data)]) + data
    bluez.hci_send_cmd(sock, 0x08, 0x0008, param)

def _set_advertise_enable(sock, enable):
    param = b'\x01' if enable else b'\x00'
    bluez.hci_send_cmd(sock, 0x08, 0x000a, param)

def transmit(id, signal, value, interval = 0x00a0, duration = 0.5):
    id = id & 0xff
    hash = binascii.crc32(signal.encode())
    header = struct.pack('<BBBBL', 0xff, 0x03, 0x97, id, hash)
    data = header + value.encode()[:23]

    sock = bluez.hci_open_dev(0)
    _set_advertising_parameters(sock, interval)
    _set_advertising_data(sock, data)
    _set_advertise_enable(sock, True)
    time.sleep(duration)
    _set_advertise_enable(sock, False)

if __name__ == "__main__":
    import sys
    transmit(int(sys.argv[1]), sys.argv[2], sys.argv[3])
