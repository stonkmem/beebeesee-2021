from pathlib import Path
import statistics as stats
from threading import Thread
from typing import *
import cv2
import face_recognition as frec
import numpy as np
import PIL as pil
from ..info import MODELS_DIR
from .ml import create_prototype_emotion_model


Image = np.ndarray
CropData = Tuple[int, int, int, int]


emotion_model = create_prototype_emotion_model()
emotion_model.load_weights(MODELS_DIR / "trained_model.h5")

cv2.ocl.setUseOpenCL(False)
emotion_dict = {
    0: "Angry",
    1: "Disgusted",
    2: "Fearful",
    3: "Happy",
    4: "Neutral",
    5: "Sad",
    6: "Surprised"
}
emotion_hash: Dict[int, str] = {hash(s): s for s in emotion_dict.values()}
"""
Get the feeling as a string from its hash value.
"""


def open_image(filepath: Path) -> Image:
    """
    Load an image into a memory with its path.
    """
    return frec.load_image_file(filepath)


def preprocess(image: Image) -> Image:
    """
    Resize the image.
    """
    image = cv2.resize(image, (600, 500))
    image = cv2.flip(image, -1)
    return image


def find_faces(image: Image) -> Iterable[CropData]:
    """
    Get a list of the location of each face found in an image.
    """
    detector = cv2.CascadeClassifier(
        str(
            MODELS_DIR / "haarcascades" / "haarcascade_frontalface_default.xml"
        )
    )
    grayscale_image: Image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return detector.detectMultiScale(
        grayscale_image,
        scaleFactor=1.3,
        minNeighbors=5
    )


def crop(image: Image, location: CropData) -> Image:
    """
    Crop the image using the location data found from `find_faces`.
    """
    x, y, w, h = location
    return image[y:y + h, x:x + w]


def convert_face(face: Image) -> Image:
    cheese = np.array(
        pil.Image.fromarray(face).convert("L").resize(
            (48, 48), pil.Image.ANTIALIAS
        )
    )
    return np.reshape(cheese, (1, 48, 48, 1))


def classify(image: Image, location: CropData) -> np.ndarray:
    """
    Get a list of each emotion and confidence level from each face.
    """
    face: Image = crop(image, location)
    #print(f"[beebeesee.util.fr.classify] face_before: {face}")
    face = convert_face(face)
    #cv2.imshow("after intense editing", face)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #print(f"[beebeesee.util.fr.classify] face_after: {face}")
    #print(f"[beebeesee.util.fr.classify] face.ndim: {face.ndim}")
    return emotion_model.predict(face)


def resolve_classification(classification: np.ndarray) -> str:
    """
    Get the most confident emotion.
    """
    return emotion_dict[np.argmax(classification)]


def classify_multiple(
    image: Image, locations: Iterable[CropData]
) -> Iterable[str]:
    """
    Classify all faces found in an image.
    """
    emotions: List[str] = []
    for location in locations:
        classification: np.ndarray = classify(image, location)
        emotion: str = resolve_classification(classification)
        emotions.append(emotion)
    return emotions


def consensus(feelings: Iterable[str]) -> str:
    """
    Return a unanimous feeling.
    """
    hashed: int = [hash(s) for s in feelings]
    mode: int = stats.mode(hashed)
    return emotion_hash[mode]


def _show_image(image: Image) -> None:
    cv2.imshow("image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def predict(filepath: Path) -> str:
    """
    Get the general emotion of the audience from an image of them located
    at `filepath`.
    """
    image = open_image(filepath)
    #print(f"OPEN_IMAGE: {image}")
    image = preprocess(image)
    #print(f"PREPROCESS: {image}")
    faces = find_faces(image)
    print(f"FIND_FACES: {faces}")
    emotions = classify_multiple(image, faces)
    return consensus(emotions)
