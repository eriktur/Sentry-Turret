import serial_comm

def init_serial():
    # Initialiserer serialforbindelsen via serial_comm (brukes av begge moduler)
    return serial_comm.init_serial()

def on_label_move(event):
    x, y = event.x, event.y
    print(f"[MOUSE_MOVE] Moved to X={x}, Y={y}")
    ser = serial_comm.ser
    if ser:
        cmd = f"{x},{y}\n"
        ser.write(cmd.encode('utf-8'))
        print(f"[DEBUG] Sent: {cmd.strip()}")
    else:
        print("[ERROR] Serial connection not initialized.")

def mouse_move_logic(frame, shared_state):
    import cv2
    # Bruk musekoordinatene lagret i shared_state
    mx = shared_state.get('mouse_x', 0)
    my = shared_state.get('mouse_y', 0)
    cv2.circle(frame, (mx, my), 5, (0, 0, 255), -1)
    cv2.putText(frame, "Mouse Move Mode", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return frame
