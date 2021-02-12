"""
Module for training the models.
ONLY run once, before deploying the code.

This may take several hours to run, especially if you are not running
this on a GPU.
"""
import tensorflow as tf

from ocr_model import OCRModel
from noise_remover import DenoisingAutoencoder

# configure tensorflow for running on GPU, if you are running on cpu, comment these lines
config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(allow_growth=True))
sess = tf.compat.v1.Session(config=config)

# initialize OCR model
ocr_model = OCRModel()
ocr_model.build_model()
# train and save the model to disk
ocr_model.train_model()
ocr_model.save_model()

# initialize denoising model
denoiser = DenoisingAutoencoder()
# build and train the autoencoder
denoiser.build_model()
denoiser.train_model()
# save the model
denoiser.save_model()
