from glob import glob
from random import shuffle
import os

emotions = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
n = 1000


for emotion in emotions:
    files = glob(f"train/{emotion}/*.jpg") + glob(f"test/{emotion}/*.jpg")
    shuffle(files)
    os.chdir("data")
    os.mkdir(emotion)
    os.chdir("..")

    for filename in files[:n]:
        filename = filename.replace("\\", "/")
        with open(filename, "rb") as readfile:
            data = readfile.read()

        new_filename = f"data/{emotion}/" + filename.split("/")[-1]
        with open(new_filename, "wb+") as writefile:
            writefile.write(data)
