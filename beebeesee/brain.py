from pathlib import Path
import cv2
import face_recognition as frec
import tensorflow as tf
import tensorflow.keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from .info import MODELS_DIR


def create_prototype_emotion_model():
    emotion_model = Sequential()
    emotion_model.add(Conv2D(32, kernel_size=(
        3, 3), activation='relu', input_shape=(48, 48, 1)))
    emotion_model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
    emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
    emotion_model.add(Dropout(0.25))
    emotion_model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
    emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
    emotion_model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
    emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
    emotion_model.add(Dropout(0.25))
    emotion_model.add(Flatten())
    emotion_model.add(Dense(1024, activation='relu'))
    emotion_model.add(Dropout(0.5))
    emotion_model.add(Dense(7, activation='softmax'))
    return emotion_model


MODELS_FILE = MODELS_DIR / "trained_model.h5"
MODEL = create_prototype_emotion_model()
MODEL.load_weights(MODELS_FILE)


def predict(filepath: Path):
    image = cv2.imread(str(filepath), -1)
    cv2.imshow("image", image)
    face_locations = frec.face_locations(image)
