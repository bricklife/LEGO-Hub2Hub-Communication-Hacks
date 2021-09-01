import bluetooth._bluetooth as bluez
import binascii
import struct
import time

OGF_LE_CTL = 0x08

OCF_LE_SET_ADVERTISING_PARAMETERS   = 0x0006
OCF_LE_SET_ADVERTISING_DATA         = 0x0008
OCF_LE_SET_ADVERTISE_ENABLE         = 0x000a
OCF_LE_SET_SCAN_PARAMETERS          = 0x000b
OCF_LE_SET_SCAN_ENABLE              = 0x000c

EVT_LE_META_EVENT           = 0x3e
EVT_LE_ADVERTISING_REPORT   = 0x02

ADV_SCAN_IND = 0x02

def _set_advertising_parameters(sock, interval):
    interval = interval & 0xffff
    if interval < 0x00a0:
        interval = 0x00a0 # shall not be set to less than 0x00A0 (100 ms) if the Advertising_Type is set to 0x02 (ADV_SCAN_IND) 
    type = ADV_SCAN_IND
    param = struct.pack('<HHBBB6sBB', interval, interval, type, 0x00, 0x00, b'', 0b00000111, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_PARAMETERS, param)

def _set_advertising_data(sock, data):
    data = data[:31]
    param = bytes([len(data)]) + data
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_DATA, param)

def _set_advertise_enable(sock, enable):
    param = b'\x01' if enable else b'\x00'
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISE_ENABLE, param)

def _set_scan_parameters(sock):
    param = struct.pack('<BHHBB', 0x00, 0x0010, 0x0010, 0x00, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_PARAMETERS, param)

def _set_scan_enable(sock, enable):
    le_scan_enable = 0x01 if enable else 0x00
    param = struct.pack('BB', le_scan_enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, param)

def transmit_signal(transmission_id, signal, value, interval = 0x00a0, duration = 0.5):
    transmission_id = transmission_id & 0xff
    hash = binascii.crc32(signal.encode())
    header = struct.pack('<BBBBL', 0xff, 0x03, 0x97, transmission_id, hash)
    data = header + value.encode()[:23]

    sock = bluez.hci_open_dev(0)
    _set_advertising_parameters(sock, interval)
    _set_advertising_data(sock, data)
    _set_advertise_enable(sock, True)
    time.sleep(duration)
    _set_advertise_enable(sock, False)

def receive_signal(callback):
    sock = bluez.hci_open_dev(0)

    # save current filter
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    bluez.hci_filter_set_event(flt, EVT_LE_META_EVENT)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)

    _set_scan_enable(sock, False)
    _set_scan_parameters(sock)
    _set_scan_enable(sock, True)

    transmission_id = None

    while True:
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
        if event == EVT_LE_META_EVENT:
            subevent, num = struct.unpack("BB", pkt[3:5])
            if subevent == EVT_LE_ADVERTISING_REPORT and num == 1:
                etype, dlen = struct.unpack("BxxxxxxxB", pkt[5:14])
                if etype == ADV_SCAN_IND and dlen >= 8:
                    data = pkt[14:-1]
                    if data[:3] == b'\xff\x03\x97':
                        tid, hash = struct.unpack("<xxxBL", data[:8])
                        value = data[8:].decode()
                        if tid != transmission_id:
                            callback(hash, value)
                            transmission_id = tid

    # restore old filter
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)

if __name__ == "__main__":
    import sys
    if sys.argv[1] == 'transmit':
        transmit_signal(int(sys.argv[2]), sys.argv[3], sys.argv[4])
    elif sys.argv[1] == 'receive':
        def r(hash, value):
            print(hash, value)
        receive_signal(r)
