import tkinter as tk
import numpy as np
import cv2
from PIL import ImageTk, Image
from gooey import Label, Frame, Button, Tk

from util.ml import create_prototype_emotion_model

emotion_model = create_prototype_emotion_model()
emotion_model.load_weights('../models/trained_model.h5')

cv2.ocl.setUseOpenCL(False)
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}


def modifyImg(frame_edit, frame):
    bounding_box = cv2.CascadeClassifier('../models/haarcascades/haarcascade_frontalface_default.xml')
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    num_faces = bounding_box.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in num_faces:
        cv2.rectangle(frame_edit, (x, y - 50), (x + w, y + h + 10), (255, 0, 0), 2)
        roi_gray_frame = gray_frame[y:y + h, x:x + w]
        cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)
        emotion_prediction = emotion_model.predict(cropped_img)
        maxindex = int(np.argmax(emotion_prediction))
        cv2.putText(
            frame_edit, emotion_dict[maxindex],
            (x + 20, y - 60), cv2.FONT_HERSHEY_SIMPLEX, 1,
            (255, 255, 255), 2, cv2.LINE_AA
        )
    return frame_edit



class SentimentalWebcam(Frame):
    def __init__(self, master=None):
        self.master = Tk() if master else master
        Frame.__init__(self, self.master, bg="white")
        self.root = Frame(master, bg="white")

        self.cap = cv2.VideoCapture(0)
        flag, frame = self.cap.read()
        frame = cv2.resize(frame, (600, 500))
        self.img = cv2.flip(frame, 1)

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

        self.boolean = True
        self.dt = 0
        self.playImg()

        if not master:
            self.pack(fill=tk.BOTH, expand=1)
            self.master.mainloop()

    def playImg(self):
        flag, frame = self.cap.read()
        frame = cv2.resize(frame, (600, 500))
        frame = cv2.flip(frame, 1)

        if self.dt == 500:
            self.img, frame = frame, modifyImg(frame, self.img)
            self.dt = 0

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        frame = cv2.resize(frame, (800, 600))

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        if self.boolean:
            self.dt += 10
            self.lmain.after(10, self.playImg)

    def pack(self, *args, **kwargs):
        self.root.pack(*args, **kwargs)

    def toggle_show(self):
        self.boolean = not self.boolean
        self.playImg()


if __name__ == "__main__":
    SentimentalWebcam()