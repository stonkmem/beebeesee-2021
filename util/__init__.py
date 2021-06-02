import tkinter as tk
import cv2
from PIL import ImageTk, Image


class Webcam(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="white")
        self.root = tk.Frame(master, bg="white")
        width, height = 800, 600
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        label = tk.Label(
            self.root,
            text="Webcam Footage",
            fg="red",
            font=("Trebuchet MS", 15),
            bg="white",
        )
        label.pack(side=tk.TOP)
        self.lmain = tk.Label(self.root)
        self.lmain.pack(fill=tk.BOTH, expand=1, side=tk.TOP)
        tk.Button(
            self.root,
            text="Play",
            bg="#19A7A7",
            fg="white",
            command=self.toggle_show,
        ).pack(side=tk.BOTTOM)
        self.boolean = False

        _, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)

    def pack(self, *args, **kwargs):
        self.root.pack(*args, **kwargs)

    def toggle_show(self):
        self.boolean = not self.boolean
        self.show()

    def show(self):
        _, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        if self.boolean:
            self.lmain.after(10, self.show)
