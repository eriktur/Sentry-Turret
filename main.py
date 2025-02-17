import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import mouse_click
import mouse_move
import object_detect
import serial_comm

class RobotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Controller")
        self.root.geometry("1000x600")

        self.shared_state = {
            "selected_object": "Face",
            "selected_color": "Blue",
            "mouse_x": 0,
            "mouse_y": 0
        }

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.control_frame = ttk.Frame(self.main_frame, width=300)
        self.control_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.video_frame = ttk.Frame(self.main_frame)
        self.video_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack()

        self.mode = tk.StringVar(value="mouse_click")

        ttk.Label(self.control_frame, text="Select mode:", font=("Arial", 12, "bold")).pack(pady=5)

        self.mouse_click_btn = ttk.Button(self.control_frame, text="Mouse Click Tracking",
                                          command=self.set_mode_mouse_click)
        self.mouse_click_btn.pack(fill="x", pady=5)

        self.mouse_move_btn = ttk.Button(self.control_frame, text="Mouse Move Tracking",
                                         command=self.set_mode_mouse_move)
        self.mouse_move_btn.pack(fill="x", pady=5)

        self.object_detect_btn = ttk.Button(self.control_frame, text="Object Detection",
                                            command=self.set_mode_object_detect)
        self.object_detect_btn.pack(fill="x", pady=5)


        self.object_options = ["Face", "Ball", "Color Tracking"]
        self.selected_object = tk.StringVar(value=self.object_options[0])

        self.object_dropdown_label = ttk.Label(self.control_frame, text="Select object:")
        self.object_dropdown = ttk.Combobox(self.control_frame, textvariable=self.selected_object,
                                            values=self.object_options)

        self.color_options = ["Blue", "Red", "Green", "Yellow"]
        self.selected_color = tk.StringVar(value=self.color_options[0])

        self.color_dropdown_label = ttk.Label(self.control_frame, text="Select color:")
        self.color_dropdown = ttk.Combobox(self.control_frame, textvariable=self.selected_color,
                                           values=self.color_options)

        # Start webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            exit()


        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)


        self.video_label.bind("<Button-1>", self.on_video_click)
        self.video_label.bind("<Motion>", self.on_video_motion)


        serial_comm.init_serial()

        self.update_camera()

    def on_video_click(self, event):

        self.shared_state["mouse_x"] = event.x
        self.shared_state["mouse_y"] = event.y
        if self.mode.get() == "mouse_click":
            mouse_click.on_label_click(event)
            print(f"[INFO] Video clicked at X={event.x}, Y={event.y}")

    def on_video_motion(self, event):

        self.shared_state["mouse_x"] = event.x
        self.shared_state["mouse_y"] = event.y
        if self.mode.get() == "mouse_move":
            mouse_move.on_label_move(event)

    def set_mode_mouse_click(self):
        self.mode.set("mouse_click")
        self.hide_object_controls()
        print("Mode: Mouse click.")

    def set_mode_mouse_move(self):
        self.mode.set("mouse_move")
        self.hide_object_controls()
        print("Mode: Mouse follow.")

    def set_mode_object_detect(self):
        self.mode.set("object_detect")
        self.shared_state["selected_object"] = self.selected_object.get()
        self.shared_state["selected_color"] = self.selected_color.get()
        print(f"Mode: Object detection - Following: {self.shared_state['selected_object']} - Color: {self.shared_state['selected_color']}")

        self.object_dropdown_label.pack(pady=5)
        self.object_dropdown.pack(pady=5)

        if self.selected_object.get() == "Color Tracking":
            self.color_dropdown_label.pack(pady=5)
            self.color_dropdown.pack(pady=5)

        self.object_dropdown.bind("<<ComboboxSelected>>", self.on_object_selected)

    def on_object_selected(self, event=None):
        self.shared_state["selected_object"] = self.selected_object.get()
        print(f"Chosen object: {self.shared_state['selected_object']}")
        if self.selected_object.get() == "Color Tracking":
            self.color_dropdown_label.pack(pady=5)
            self.color_dropdown.pack(pady=5)
        else:
            self.color_dropdown_label.pack_forget()
            self.color_dropdown.pack_forget()

    def hide_object_controls(self):
        self.object_dropdown_label.pack_forget()
        self.object_dropdown.pack_forget()
        self.color_dropdown_label.pack_forget()
        self.color_dropdown.pack_forget()

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:

            frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_LINEAR)

            if self.mode.get() == "mouse_click":
                frame = mouse_click.mouse_click_logic(frame, self.shared_state)
            elif self.mode.get() == "mouse_move":
                frame = mouse_move.mouse_move_logic(frame, self.shared_state)
            elif self.mode.get() == "object_detect":
                frame = object_detect.object_detect_logic(frame, self.shared_state)


            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
            self.video_label.config(image=imgtk)
            self.video_label.image = imgtk

        self.root.after(10, self.update_camera)

    def close(self):
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
