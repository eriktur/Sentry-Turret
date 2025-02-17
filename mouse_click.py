import serial_comm

def init_serial():

    return serial_comm.init_serial()

def on_label_click(event):
    x, y = event.x, event.y
    print(f"[MOUSE_CLICK] Clicked at X={x}, Y={y}")
    ser = serial_comm.ser
    if ser:
        cmd = f"{x},{y}\n"
        ser.write(cmd.encode('utf-8'))
        print(f"[DEBUG] Sent: {cmd.strip()}")
    else:
        print("[ERROR] Serial connection not initialized.")

def mouse_click_logic(frame, shared_state):
    import cv2
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2
    return frame
