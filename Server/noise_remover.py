"""
Module used to train the noise remover model and save it to HDF5 format.
"""

import glob

import PIL
import cv2
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import InputLayer, Conv2D, MaxPooling2D, UpSampling2D
from tensorflow.keras.losses import binary_crossentropy
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.activations import relu, sigmoid

import consts
from base_model import ModelNotLoadedError, BaseTFModel, singleton, ModelNotBuiltError


@singleton
class ImageLoader:
    def __init__(self):
        self._X_train: np.array = None
        self._X_valid: np.array = None

    @staticmethod
    def _load_images(path: str) -> np.array:
        """
        Load images from computer, resize them, convert to grayscale
        and reshape them to fit into numpy arrays.

        Args:
            path (str): The path to a folder containing the images to be loaded.

        Returns:
            np.array: array containing the images.
        """

        X_imgs = []

        for image_path in glob.glob(path + '\\*'):
            try:
                # convert to grayscale and resize to predefined image size
                img = PIL.Image.open(image_path).convert('L').resize(consts.IMAGE_SIZE)
            except PIL.UnidentifiedImageError:
                continue
            img_arr = np.asarray(img).astype(np.float32)  # convert to numpy array
            img_arr = img_arr / 255  # change scale to be between 0.0 and 1.0
            X_imgs.append(img_arr)
        return np.array(X_imgs)

    def load_training_validation(self):
        """
        Load training and validation sets from computer, and transform them
        to fit the model specifications.
        """

        if self._X_train and self._X_valid:
            # images are already loaded
            return

        # load training images
        self._X_train = self._load_images(consts.TRAIN_ALL_PATH)
        print(f'Finished loading {len(self._X_train)} training images.')

        # load validation images
        self._X_valid = self._load_images(consts.VALIDATION_ALL_PATH)
        print(f'Finished loading {len(self._X_valid)} validation images.')

    @property
    def X_train(self):
        return self._X_train

    @property
    def X_valid(self):
        return self._X_valid


class DenoisingAutoencoder(BaseTFModel):
    """
    Class for building, training, and later loading a denoising autoencoder model.
    """
    LR = 1e-3
    EPOCHS = 2
    BATCH_SIZE = 128
    MODEL_NAME = 'noise_remover.h5'

    def __init__(self):
        super().__init__()
        self._image_loader: ImageLoader = ImageLoader()

    @staticmethod
    def _add_gaussian_noise(X_imgs: np.array) -> np.array:
        """
        Apply Gaussian noise to images.

        Args:
            X_imgs (np.array): The images (provided as np arrays of the shape
             defined in consts) for which to apply gaussian noise algorithm.

        Returns:
            np.array: Images after adding noise with added grayscale color channel.
        """

        gaussian_noise_imgs = []
        width, height = consts.IMAGE_SIZE

        for img in X_imgs:
            gaussian = np.random.random((width, height, 1)).astype(np.float32)
            gaussian_img = cv2.addWeighted(img, 0.75, 0.25 * gaussian, 0.25, 0)
            # add grayscale color channel
            gaussian_noise_imgs.append(np.expand_dims(gaussian_img, axis=-1))

        # convert to np array
        gaussian_noise_imgs = np.array(gaussian_noise_imgs, dtype=np.float32)

        return gaussian_noise_imgs

    def build_model(self) -> None:
        """
        Build and compile a model which acts as an autoencoder that removes
        image noise. First, we decrease the number of features of the
        image, to try and capture the most important parts of the image,
        and then we scale the image back to it's original size.
        """

        # build encoder - reducing image features
        encoder = Sequential([
            InputLayer(input_shape=consts.IMAGE_SIZE + (1,)),
            Conv2D(filters=256, kernel_size=(3, 3), activation=relu, padding='same'),
            Conv2D(filters=128, kernel_size=(3, 3), activation=relu, padding='same'),
            MaxPooling2D(pool_size=(2, 2), padding='same'),
            Conv2D(filters=64, kernel_size=(3, 3), activation=relu, padding='same'),
            Conv2D(filters=32, kernel_size=(3, 3), activation=relu, padding='same'),
            MaxPooling2D(pool_size=(2, 2), padding='same'),
            Conv2D(filters=32, kernel_size=(3, 3), activation=relu, padding='same'),
            MaxPooling2D(pool_size=(2, 2), padding='same'),
        ])

        # build decoder - upscaling back to original size and trying to recreate
        # original image, without the noise
        decoder = Sequential([
            InputLayer(input_shape=(consts.IMAGE_SIZE[0] // 8, consts.IMAGE_SIZE[1] // 8, 32)),
            Conv2D(filters=32, kernel_size=(3, 3), activation=relu, padding='same'),
            UpSampling2D((2, 2)),
            Conv2D(filters=64, kernel_size=(3, 3), activation=relu, padding='same'),
            Conv2D(filters=128, kernel_size=(3, 3), activation=relu, padding='same'),
            UpSampling2D((2, 2)),
            Conv2D(filters=256, kernel_size=(3, 3), activation=relu, padding='same'),
            UpSampling2D((2, 2)),
            Conv2D(filters=1, kernel_size=(3, 3), activation=sigmoid, padding='same')
        ])

        # combine both models together to create the autoencoder
        model = Sequential([encoder, decoder])

        # compile the model topography into code that TensorFlow can efficiently
        # execute. Configure training to minimize the model's binary crossentropy loss
        model.compile(loss=binary_crossentropy,
                      optimizer=Adam(learning_rate=self.LR),
                      metrics=['accuracy'])
        self._model = model
        self._model_built = True

    def train_model(self) -> None:
        """
        Train the autoencoder with the train and validation sets of images
        and log training progress to disk.

        Raises:
            ModelNotBuiltError: when trying to train an un built model.
        """

        if not self._model_built:
            raise ModelNotBuiltError('The model has to be built before training it.')

        # load training and validation data from disk and preprocess them
        self._image_loader.load_training_validation()
        X_train, X_valid = self._image_loader.X_train, self._image_loader.X_valid

        # add noise for the model to try and remove
        X_train_noisy = self._add_gaussian_noise(X_train)
        X_valid_noisy = self._add_gaussian_noise(X_valid)

        # train the model
        self._model.fit(X_train_noisy, X_train,
                        epochs=self.EPOCHS,
                        verbose=1,
                        batch_size=self.BATCH_SIZE,
                        validation_data=(X_valid_noisy, X_valid))

    def save_model(self) -> None:
        """Save the model to disk as a HDF5 file."""
        self._model.save(self.MODEL_NAME)

    def load_model(self) -> None:
        """Load the model from disk into memory."""
        self._model = load_model(self.MODEL_NAME)
        self._model_loaded = True

    def denoise_image(self, img: np.array) -> np.array:
        """
        Use the denoising autoencoder in order to remove noise from the image.

        Args:
            img (np.array): The image to denoise (image shape needs to be the
             size defined in consts, yet the image does not have to include a
              grayscale color channel).
        Returns:
            np.array: The denoised image as np array of shape `(*consts.IMAGE_SIZE, 1)`.
        Raises:
            ModelNotLoadedError: If the autoencoder was not loaded before
              trying to denoise image.
            ValueError: In case the specified image has incorrect shape.
        """

        if not self._model_loaded:
            raise ModelNotLoadedError('You have to load the model before'
                                      ' trying to denoise image')
        if img.shape != consts.IMAGE_SIZE and img.shape != consts.IMAGE_SIZE + (1,):
            raise ValueError(f'Image shape must be {consts.IMAGE_SIZE} '
                             f'or {consts.IMAGE_SIZE + (1,)}')

        if img.max() > 1.0:
            # assuming that if values are not between 0.0 and 1.0,
            # they are in range 0 to 255, therefore rescale image to fit into model
            img = img / 255

        # reshape the image to fit into the model
        img = img.reshape(consts.IMAGE_SIZE + (1,))
        # define batch with only one image
        batch = np.expand_dims(img, axis=0)
        # perform denoising
        denoised = self._model(batch)
        # reshape the image back to it's original shape
        denoised = np.expand_dims(denoised.numpy().squeeze(), axis=-1)

        return denoised

    def evaluate(self, images):
        """Evaluate the model and calculate accuracy and loss."""
        return self._model.evaluate(images)
