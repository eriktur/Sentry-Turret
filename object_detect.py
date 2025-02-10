import cv2
import numpy as np
import serial_comm  # Bruker den delte serial-modulen

# Last inn Haar-cascade for ansiktsdeteksjon
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# HSV-farger for fargetracking
COLOR_RANGES = {
    "Blue": ([100, 150, 50], [140, 255, 255]),
    "Red": ([0, 150, 50], [10, 255, 255]),
    "Green": ([40, 50, 50], [90, 255, 255]),
    "Yellow": ([20, 100, 100], [30, 255, 255])
}

def object_detect_logic(frame, shared_state):
    selected_object = shared_state.get("selected_object", "Face")
    detected_center = None

    if selected_object == "Face":
        frame, detected_center = detect_faces(frame)
    elif selected_object == "Ball":
        frame, detected_center = detect_ball(frame)
    elif selected_object == "Color Tracking":
        selected_color = shared_state.get("selected_color", "Blue")
        frame, detected_center = detect_color(frame, selected_color)

    # Hvis et objekt er funnet, oppdater shared_state og send koordinatene via serial
    if detected_center is not None:
        center_x, center_y = detected_center
        shared_state["object_x"] = center_x
        shared_state["object_y"] = center_y
        # Send til Arduino via serial (hvis tilkoblingen er oppe)
        if serial_comm.ser:
            cmd = f"{center_x},{center_y}\n"
            serial_comm.ser.write(cmd.encode("utf-8"))
            print(f"[OBJECT DETECT] Sent: {cmd.strip()}")
        else:
            print("[ERROR] Serial connection not initialized.")
    return frame

def detect_faces(frame):
    """Oppdager ansikter, tegner rektangel og beregner senter av det første funnet ansiktet."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    detected_center = None

    if len(faces) > 0:
        # Velg det første ansiktet (alternativt kan du velge det største)
        (x, y, w, h) = faces[0]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        center_x = x + w // 2
        center_y = y + h // 2
        cv2.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)
        detected_center = (center_x, center_y)
    return frame, detected_center

def detect_color(frame, selected_color):
    """Oppdager objekter med en spesifikk farge, tegner rektangel og beregner senter."""
    lower, upper = COLOR_RANGES[selected_color]
    lower = np.array(lower, dtype=np.uint8)
    upper = np.array(upper, dtype=np.uint8)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, lower, upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detected_center = None

    for contour in contours:
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, selected_color, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # Bruk den første konturen som oppfyller kriteriet
            detected_center = (x + w // 2, y + h // 2)
            cv2.circle(frame, (x + w // 2, y + h // 2), 5, (255, 0, 0), -1)
            break  # Kun det første objektet
    return frame, detected_center

def detect_ball(frame):
    """Oppdager en ball ved hjelp av HoughCircles, tegner sirkel og beregner senter."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_orange = np.array([5, 100, 100])
    upper_orange = np.array([15, 255, 255])
    mask = cv2.inRange(hsv, lower_orange, upper_orange)
    blurred = cv2.GaussianBlur(mask, (9, 9), 2)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 50,
                               param1=50, param2=30, minRadius=10, maxRadius=100)
    detected_center = None

    if circles is not None:
        circles = np.uint16(np.around(circles))
        # Tegn alle sirkler, men bruk den første for koordinatene
        for i in circles[0, :]:
            cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
            cv2.putText(frame, "Ball", (i[0] - 20, i[1] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        detected_center = (circles[0, 0], circles[0, 1])
    return frame, detected_center
