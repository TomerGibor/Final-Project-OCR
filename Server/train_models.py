"""
Module for training the models.
Only need run once, before deploying the application.

This may take several hours to run, especially if you are not running
this on a dedicated GPU.
"""
import config_tf
from ocr_model import OCRModel
from noise_remover import DenoisingAutoencoder

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
