"""
Module for building OCR model, training it and performing predictions.
"""
from datetime import datetime

import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import (Dense, Conv2D, Flatten, MaxPooling2D,
                                     Dropout, InputLayer)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator, DirectoryIterator
from tensorflow.keras.losses import categorical_crossentropy
from tensorflow.keras.activations import relu, softmax
from tensorflow.keras.callbacks import (CSVLogger, TensorBoard,
                                        EarlyStopping, ModelCheckpoint, Callback)

import config_tf
import consts
from base_model import ModelNotLoadedError, ModelNotBuiltError, BaseTFModel
from model_evaluator import ModelEvaluator


class OCRModel(BaseTFModel):
    """
    Class used for building and training a model which is able to
    distinguish between different characters using ML and TensorFlow.
    """
    BATCH_SIZE = 32
    LR = 3e-4
    MAX_EPOCHS = 35
    MODEL_NAME = 'ocr_model.h5'
    TENSORBOARD_DIR = 'D:\\Keras\\tensorboard'
    LOG_DIR = 'logs\\training-history'
    CHECKPOINT_DIR = 'D:\\Keras\\models\\training'

    def __init__(self):
        super().__init__()

    def build_model(self) -> None:
        """
        Build and compile a sequential ML model using TensorFlow to detect
        a single character with convolutional layers, max pooling layers,
        and fully-connected layers.
        """

        # build ML model to detect a single character by using CNN, max pooling
        # and fully connected layers
        model = Sequential()

        # add input layer that receives a gray-scale image of predefined size
        model.add(InputLayer(input_shape=consts.IMAGE_SIZE + (1,)))
        # add convolutional layers with zero-padding (in order to retain
        # image size) and rectified linear unit activations
        model.add(Conv2D(filters=32, kernel_size=(3, 3), activation=relu, padding='same'))
        model.add(Conv2D(filters=64, kernel_size=(3, 3), activation=relu, padding='same'))
        # add max pooling layer to reduce image dimensions by a factor of 2 (reduce
        # total size by 4) and remove unwanted noise
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

        # add another set of convolutional and max pooling layers, while
        # increasing the amount of filters per layer
        model.add(Conv2D(filters=128, kernel_size=(3, 3), activation=relu, padding='same'))
        # add dropout layer to prevent overfitting
        model.add(Dropout(0.15))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

        model.add(Conv2D(filters=256, kernel_size=(3, 3), activation=relu, padding='same'))
        model.add(Dropout(0.15))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

        # flatten the output from max pooling layer (2D output) into a
        # one-dimensional tensor
        model.add(Flatten())

        # add fully-connected layer after flattening and another dropout layer that
        # randomly turns off some percentage of neurons
        model.add(Dense(units=256, activation=relu))
        model.add(Dropout(0.40625))

        # add final output layer with 36 nodes (26 letters + 10 digits) with
        # activation of softmax to determine the probability of the input image
        # being some character
        model.add(Dense(units=36, activation=softmax))

        print(model.summary())

        # compile the model topography, set loss function, optimizer, and learning rate
        model.compile(optimizer=Adam(learning_rate=self.LR),
                      loss=categorical_crossentropy,
                      metrics=['accuracy'])

        self._model = model
        self._model_built = True

    def train_model(self) -> None:
        """
        Train the model using training set and validation set and log training
        progress to disk.

        Raises:
            ModelNotBuiltError: when trying to train an un built model.
        """
        if not self._model_built:
            raise ModelNotBuiltError('The model has to be built before training it.')

        training_data, validation_data = self._load_data()
        self._model.fit(training_data,
                        epochs=self.MAX_EPOCHS,
                        verbose=1,
                        validation_data=validation_data,
                        callbacks=self._setup_training_callbacks())
        self._model_loaded = True

    def save_model(self) -> None:
        """Save the model to disk as a HDF5 file."""
        self._model.save(self.MODEL_NAME)

    def load_model(self) -> None:
        """Load the model from disk into memory."""
        self._model = load_model(self.MODEL_NAME)
        self._model_loaded = True

    def predict(self, img: np.array) -> np.array:
        """
        Function used to predict probabilities of an image of a character
        belonging to any specific character.

        Args:
            img (np.array): An image of a character of which to perform the
                prediction (image shape needs to be the size defined in consts,
                yet the image does not have to include a grayscale color channel).
        Returns:
            np.array: The probabilities of the image being of any character.
        Raises:
            ModelNotLoadedError: If model was not loaded before trying to predict.
            ValueError: In case the specified image has incorrect shape.
        """

        if not self._model_loaded:
            raise ModelNotLoadedError('You have to load the model before'
                                      ' performing predictions')
        if img.shape != consts.IMAGE_SIZE and img.shape != consts.IMAGE_SIZE + (1,):
            raise ValueError(f'Image shape must be {consts.IMAGE_SIZE}'
                             f'or {consts.IMAGE_SIZE + (1,)}')

        if img.max() > 1.0:
            # assuming that if values are not between 0.0 and 1.0,
            # they are in range 0 to 255, therefore rescale image to fit into model
            img = img / 255

        # reshape the image to fit into the model
        img = img.reshape(consts.IMAGE_SIZE + (1,))
        # define batch with only one image
        batch = np.expand_dims(img, axis=0)
        # perform prediction
        predictions = self._model.predict(batch)
        return predictions

    def evaluate(self, *, images: np.ndarray = None, folder_path: str = None) -> None:
        """
        Evaluate the model: calculate accuracy, show confusion matrix
        and print classification report. Works with either the images
        provided, or the path to these images. If none of them are
        provided, use the default test images path.
        """
        if not self._model_loaded:
            raise ModelNotLoadedError('You have to load the model before evaluating it.')

        evaluator = ModelEvaluator(self._model, images=images, folder_path=folder_path)
        evaluator.evaluate()

    def _load_data(self) -> tuple[DirectoryIterator, DirectoryIterator]:
        # use the ImageDataGenerator class to rescale pixel values to be between
        # 0.0 and 1.0 and randomly augment some percentage of images to decrease
        # overfitting and improve model performance over new test sets
        train_generator = ImageDataGenerator(rescale=1 / 255,
                                             shear_range=0.15,
                                             zoom_range=0.15)

        # load images from disk, convert to grayscale, resize them
        # and assign them appropriate labels
        training_data = train_generator.flow_from_directory(
            directory=consts.TRAIN_CATEGORICAL_PATH,
            target_size=consts.IMAGE_SIZE,
            classes=consts.CLASSES,
            shuffle=True,
            batch_size=self.BATCH_SIZE,
            color_mode='grayscale',
            class_mode='categorical'
        )

        validation_generator = ImageDataGenerator(rescale=1 / 255)
        validation_data = validation_generator.flow_from_directory(
            directory=consts.VALIDATION_CATEGORICAL_PATH,
            target_size=consts.IMAGE_SIZE,
            classes=consts.CLASSES,
            shuffle=False,
            batch_size=self.BATCH_SIZE,
            color_mode='grayscale',
            class_mode='categorical'
        )

        return training_data, validation_data

    def _setup_training_callbacks(self) -> list[Callback]:
        # setup TensorBoard and csv logger of training stage
        time = datetime.now().strftime(consts.DATETIME_FORMAT)
        csv_logger = CSVLogger(f'{self.LOG_DIR}-{time}.csv',
                               separator=',', append=False)
        tensorboard = TensorBoard(log_dir=f'{self.TENSORBOARD_DIR}\\fit-{time}',
                                  histogram_freq=1,
                                  write_graph=True,
                                  write_images=True,
                                  update_freq='epoch',
                                  profile_batch=2,
                                  embeddings_freq=1)

        # setup early stopping to prevent overfitting and stop training stage
        # when validation accuracy starts to decrease
        early_stop = EarlyStopping(monitor='val_accuracy', patience=7, mode='max',
                                   restore_best_weights=True)
        model_checkpoint = ModelCheckpoint(
            filepath=self.CHECKPOINT_DIR + '\\model-epoch{epoch:02d}-acc-{val_accuracy:4f}.h5',
            monitor='val_accuracy')

        return [csv_logger, tensorboard, early_stop, model_checkpoint]
