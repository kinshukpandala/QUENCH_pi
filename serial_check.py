import serial.tools.list_ports

def is_serial_connected():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.device or "ttyUSB" in port.device:
            return True
    return False
