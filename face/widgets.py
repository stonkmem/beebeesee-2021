import tkinter as tk
from tkinter import ttk
import cv2
from PIL import ImageTk, Image


class SentimentalWebcam(ttk.Frame):
    def __init__(self, master=None):
        self.master = tk.Tk() if master else master
        ttk.Frame.__init__(self, self.master, bg="white")
        self.root = ttk.Frame(master, bg="white")
        width, height = 800, 600
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        label = ttk.Label(
            self.root,
            text="Webcam Footage",
            fg="red",
            font=("Trebuchet MS", 15),
            bg="white",
        )
        label.pack(side=tk.TOP)
        self.lmain = ttk.Label(self.root)
        self.lmain.pack(fill=tk.BOTH, expand=1, side=tk.TOP)
        ttk.Button(
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

        self.img = cs2image


        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)

        if master:
            self.pack(fill=BOTH, expand=1)
            self.master.mainloop()

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

if __name__ == "__main__":
    SentimentalWebcam()