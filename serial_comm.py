import serial

SERIAL_PORT = "/dev/tty.usbmodem48CA435C64342"
BAUD_RATE = 9600

ser = None

def init_serial():
    global ser
    if ser is None:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"[INFO] Connected to {SERIAL_PORT} @ {BAUD_RATE} baud")
        except serial.SerialException as e:
            print(f"[ERROR] Could not open port {SERIAL_PORT}: {e}")
            ser = None
    return ser
