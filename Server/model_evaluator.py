"""Module used for creating a class that evaluates a model."""
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix, classification_report, plot_confusion_matrix
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import consts


class ModelEvaluator:
    """
    Class used for evaluating a model, calculating it's accuracy,
    plotting the confusion matrix, and printing the classification report.
    """
    def __init__(self, model: Sequential, *, images: np.ndarray = None, folder_path: str = None):
        if images is None:
            if not folder_path:
                print(f'No images or path specified, using default path: {consts.TEST_CATEGORICAL_PATH}')
                folder_path = consts.TEST_CATEGORICAL_PATH
            # load the images
            img_gen = ImageDataGenerator(rescale=1 / 255)
            images = img_gen.flow_from_directory(
                directory=folder_path,
                target_size=consts.IMAGE_SIZE,
                classes=consts.CLASSES,
                shuffle=False,
                color_mode='grayscale',
                class_mode='categorical'
            )
        self._images = images
        # save the predictions over the images, to later analyse them
        self._pred = model.predict(images, verbose=1)
        self._pred = np.argmax(self._pred, axis=1)

    def _calc_accuracy(self) -> None:
        true_preds = [p for p, c in zip(self._pred, self._images.classes) if p == c]
        acc = len(true_preds) / len(self._pred) * 100
        print(f'Accuracy is: {acc:.2f}%')

    def _show_cm(self) -> None:
        """Show the confusion matrix as a heat-map plot, and save it as a PNG file."""
        cm = confusion_matrix(y_true=self._images.classes, y_pred=self._pred)
        ax = plt.subplot()
        sns.heatmap(cm, ax=ax, cmap=plt.cm.Blues)
        ax.set_title('Confusion Matrix')
        ax.set_xticklabels(consts.CLASSES[::2])
        ax.set_yticklabels(consts.CLASSES[::2])
        ax.set_xlabel('Predicted label')
        ax.set_ylabel('True label')
        plt.savefig(f'{consts.EVALUATION_RESULTS_DIR}\\confusion_matrix.png')
        plt.show()

    def _print_cr(self) -> None:
        """Prettify classification report, print it, and save it as csv."""
        cr = classification_report(y_true=self._images.classes, y_pred=self._pred)
        lines = cr.split('\n')
        columns = ['character'] + [c for c in lines[0].split(' ') if c]
        df = pd.DataFrame(index=consts.CLASSES, columns=columns, dtype='float32')
        for i, line in enumerate(lines[2: len(consts.CLASSES) + 2]):
            data = [float(a) for a in line.split(' ') if a][1:]
            df.iloc[i] = [consts.CLASSES[i]] + data
        df = df.set_index('character')
        print(df)
        df.to_csv(f'{consts.EVALUATION_RESULTS_DIR}\\classification_report.csv')

    def evaluate(self) -> None:
        self._calc_accuracy()
        self._show_cm()
        self._print_cr()
