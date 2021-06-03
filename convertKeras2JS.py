import tensorflowjs as tfjs
from util.ml import create_prototype_emotion_model

emotion_model = create_prototype_emotion_model()
emotion_model.load_weights('models/trained_model.h5')

tfjs.converters.save_keras_model(emotion_model, "models/model")