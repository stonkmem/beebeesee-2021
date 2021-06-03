import tensorflow as tf
from info import MODELS_DIR


MODELS_FILE = MODELS_DIR / "trained_model.h5"
MODEL = tf.keras.Model()
MODEL.built = True
MODEL.load_weights(MODELS_FILE)
MODEL.summary()
