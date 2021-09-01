import bluetooth._bluetooth as bluez
import binascii
import struct
import time

OGF_LE_CTL = 0x08

OCF_LE_SET_ADVERTISING_PARAMETERS = 0x0006
OCF_LE_SET_ADVERTISING_DATA = 0x0008
OCF_LE_SET_ADVERTISE_ENABLE = 0x000a

def _set_advertising_parameters(sock, interval):
    interval = interval & 0xffff
    if interval < 0x00a0:
        interval = 0x00a0 # shall not be set to less than 0x00A0 (100 ms) if the Advertising_Type is set to 0x02 (ADV_SCAN_IND) 
    type = 0x02 # ADV_SCAN_IND
    param = struct.pack('<HHBBB6sBB', interval, interval, type, 0, 0, b'', 7, 0)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_PARAMETERS, param)

def _set_advertising_data(sock, data):
    data = data[:31]
    param = bytes([len(data)]) + data
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_DATA, param)

def _set_advertise_enable(sock, enable):
    param = b'\x01' if enable else b'\x00'
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISE_ENABLE, param)

def transmit_signal(transmission_id, signal, value, interval = 0x00a0, duration = 0.5):
    transmission_id = transmission_id & 0xff
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
    transmit_signal(int(sys.argv[1]), sys.argv[2], sys.argv[3])
