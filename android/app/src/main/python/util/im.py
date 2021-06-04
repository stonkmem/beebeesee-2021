import cv2
from np.magic import np
import numpy
from skimage.color import rgb2gray, gray2rgb
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu, threshold_local
from skimage.filters import try_all_threshold


def readAndShow(path: str):
    img = cv2.imread(path)
    cv2.imshow("Image", img)
    cv2.waitKey(0)


def showImage(image, title="Image", cmap_type="gray"):
    plt.imshow(image, cmap=cmap_type)
    plt.title(title)
    plt.axis("off")
    plt.show()


def retrieveRed(img):
    return img[:, :, 0]


def retrieveGreen(img):
    return img[:, :, 1]


def retrieveBlue(img):
    return img[:, :, 2]


# def BRGToBGR(path, img):
#     b, r, g = cv2.split(img)
#     img2 = cv2.merge((b, g, r))
#     cv2.imshow('Image... but with Red and Green Swapped', img2)
#     cv2.waitKey(0)
#     arr = path.split(".")
#     path_new = ".".join(arr[:-1]) + "altered" + arr[-1]
#     cv2.imwrite(path_new, img2)


def laplacian(img):
    return cv2.Laplacian(img, cv2.CV_64F)


def sobelX64(img):
    return cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5)


def sobelY64(img):
    return cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5)


def facialDetection(image):
    (h, w) = image.shape[:2]
    net = cv2.dnn.readNetFromCaffe(
        "../models/deploy.prototxt.txt",
        "../models/res10_300x300_ssd_iter_140000.caffemodel",
    )
    blob = cv2.dnn.blobFromImage(
        cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
    )
    confidence_threshold = 0.5

    net.setInput(blob)
    detections = net.forward()
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            text = "{:.2f}%".format(confidence * 100)
            y = startY - 10 if startY - 10 > 10 else startY + 10
            cv2.rectangle(
                image, (startX, startY), (endX, endY), (0, 0, 255), 2
            )
            cv2.putText(
                image,
                text,
                (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 255),
                2,
            )

    cv2.imshow("Output", image)
    cv2.waitKey(0)


def flipImageUp(img):
    # Flip the image in up direction
    vertically_flipped = np.flipud(img)
    showImage(vertically_flipped, "Vertically-Flipped Image")


def flipImageLeft(img):
    # Flip the image in left direction
    horizontally_flipped = np.fliplr(img)
    showImage(horizontally_flipped, "Horizontally-Flipped image")


def colorHist(color, title="Color Histogram"):
    plt.hist(color.ravel(), bins=256)
    plt.title(title)
    plt.show()


def globallyThresholdedImage(image):
    # Make the image grayscale using rgb2gray
    image_gray = rgb2gray(image)

    # Obtain the optimal threshold value with otsu
    thresh = threshold_otsu(image_gray)

    # Apply thresholding to the image
    binary = image_gray > thresh

    return binary


def locallyThresholdedImage(image, block_size=35, offset=10):
    # Obtain the optimal threshold value with otsu
    thresh = threshold_local(image, block_size, offset=offset)

    # Apply thresholding to the image
    binary = image > thresh

    return binary


def thresholdedImage(image):
    # Turn the fruits_image to grayscale
    grayscale = rgb2gray(image)

    # Use the try all method on the resulting grayscale image
    fig, ax = try_all_threshold(grayscale, verbose=False)

    # Show the resulting plots
    plt.show()
