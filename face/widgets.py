import tkinter as tk
import cv2
from PIL import ImageTk, Image
from gooey import Label, Frame, Button, Tk

from util.ml import create_prototype_emotion_model

emotion_model = create_prototype_emotion_model()
emotion_model.load_weights('../models/trained_model.h5')

cv2.ocl.setUseOpenCL(False)

class SentimentalWebcam(Frame):
    def __init__(self, master=None):
        self.master = Tk() if master else master
        Frame.__init__(self, self.master, bg="white")
        self.root = Frame(master, bg="white")

        self.cap = cv2.VideoCapture(0)

        Label(
            self.root,
            text="Webcam Footage",
            fg="red",
            font=("Trebuchet MS", 15),
            bg="white",
        ).pack(side=tk.TOP)

        self.lmain = Label(self.root, padx=50, bd=10)
        self.lmain.pack(fill=tk.BOTH, expand=1, side=tk.TOP)

        Button(
            self.root,
            text="Play",
            bg="#19A7A7",
            fg="white",
            command=self.toggle_show,
        ).pack(side=tk.BOTTOM)

        self.boolean = False

        self.playImg()

        if not master:
            self.pack(fill=tk.BOTH, expand=1)
            self.master.mainloop()

    def playImg(self):
        flag, frame = self.cap.read()
        frame = cv2.resize(frame, (600, 500))

        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        self.img = cv2image

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


if __name__ == "__main__":
    SentimentalWebcam()