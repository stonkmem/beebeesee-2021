import tensorflowjs as tfjs
import tensorflow.keras

# Load the model
model = tensorflow.keras.models.load_model(
    "models/trained_model.h5"
)  # keras_model.h5
tfjs.converters.save_keras_model(model, "models/js")