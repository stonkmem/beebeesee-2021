import tkinter as tk
import numpy as np
import cv2
from PIL import ImageTk, Image
from face.gooey import Frame, Tk
from face.gooey import Label as GooeyLabel

from util.ml import create_prototype_emotion_model

emotion_model = create_prototype_emotion_model()
emotion_model.load_weights('../models/trained_model.h5')

cv2.ocl.setUseOpenCL(False)
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

def draw_rectangle(frame, x, y, w, h):
    cv2.rectangle(frame, (x, y - 50), (x + w, y + h + 10), (255, 0, 0), 2)

def classify(gray_frame, x, y, w, h):
    roi_gray_frame = gray_frame[y:y + h, x:x + w]
    cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)
    emotion_prediction = emotion_model.predict(cropped_img)
    return int(np.argmax(emotion_prediction))

def draw_classification(frame, max_index, x, y):
    cv2.putText(
        frame, emotion_dict[max_index],
        (x + 20, y - 60), cv2.FONT_HERSHEY_SIMPLEX, 1,
        (255, 255, 255), 2, cv2.LINE_AA
    )

def modify_img(frame_new, frame_old):
    bounding_box = cv2.CascadeClassifier('../models/haarcascades/haarcascade_frontalface_default.xml')

    original_gray_frame = cv2.cvtColor(frame_old, cv2.COLOR_BGR2GRAY)
    new_gray_frame = cv2.cvtColor(frame_new, cv2.COLOR_BGR2GRAY)

    original_num_faces = bounding_box.detectMultiScale(original_gray_frame, scaleFactor=1.3, minNeighbors=5)
    new_num_faces = bounding_box.detectMultiScale(new_gray_frame, scaleFactor=1.3, minNeighbors=5)

    for i in range(min(len(original_num_faces), len(new_num_faces))):
        (x_new, y_new, w_new, h_new) = new_num_faces[i]
        if w_new > h_new: continue
        draw_rectangle(frame_new, *new_num_faces[i])
        max_index = classify(original_gray_frame, *original_num_faces[i])
        draw_classification(frame_new, max_index, *new_num_faces[i][:2])

    if len(new_num_faces) > len(original_num_faces):
        # this means we died cuz we don't have enough data-samples
        for i in range(len(original_num_faces), len(new_num_faces)):
            (x, y, w, h) = new_num_faces[i]
            if w > h: continue
            draw_rectangle(frame_new, *new_num_faces[i])
            max_index = classify(new_gray_frame, *new_num_faces[i])
            draw_classification(frame_new, max_index, *new_num_faces[i][:2])

    return frame_new

class Label(GooeyLabel):
    def pack(self, *args, **kwargs):
        super().pack(*args, **kwargs)
        return self

class SentimentalWebcam(Frame):
    def __init__(self, master=None):
        self.master = Tk() if master else master
        Frame.__init__(self, self.master, bg="white")

        self.cap = cv2.VideoCapture(0)
        flag, frame = self.cap.read()
        frame = cv2.resize(frame, (600, 500))
        self.img = cv2.flip(frame, 1)

        Label(self, text="FACE - Try it out!", fg="red", font=("Trebuchet MS", 15), bg="white").pack(side=tk.TOP)

        self.main = Label(self, padx=50, bd=10).pack(fill=tk.BOTH, expand=1, side=tk.TOP)

        self.dt = 0
        self.play_img()

        if not master:
            self.master.title("FACE - Your Own Sentimental Webcam")
            self.master.state("zoomed")
            self.pack(fill=tk.BOTH, expand=1)
            self.master.mainloop()

    def play_img(self):
        flag, frame = self.cap.read()
        frame = cv2.resize(frame, (600, 500))
        frame = cv2.flip(frame, 1)

        if self.dt == 100:
            self.img, frame = frame, modify_img(frame, frame)
            self.dt = 0
        else:
            frame = modify_img(frame, self.img)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        frame = cv2.resize(frame, (800, 600))

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.main.imgtk = imgtk
        self.main.configure(image=imgtk)

        self.dt += 10
        self.main.after(10, self.play_img)


if __name__ == "__main__":
    SentimentalWebcam()