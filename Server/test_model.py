from tensorflow.keras.models import load_model, Sequential, Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Dropout, UpSampling2D, Input
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import consts

model = load_model('models/model4_8529_64x64_full.h5')
test_batches = ImageDataGenerator(rescale=1 / 255) \
    .flow_from_directory(directory='D:\\Training Data\\Training Dataset\\test',
                         target_size=(64, 64),
                         shuffle=False,
                         color_mode='grayscale',
                         class_mode='categorical',
                         classes=consts.HEX_CLASSES)
pred = model.predict(test_batches, verbose=1)
predictions = [p.argmax() for p in pred]
cm = confusion_matrix(test_batches.classes, predictions)
plt.matshow(cm, cmap=plt.cm.Blues)


def prettify_cr(cr):
    lines = cr.split('\n')
    indexes = [c for c in consts.CHARACTERS]
    columns = [c for c in lines[0].split(' ') if c]
    df = pd.DataFrame(index=indexes, columns=columns, dtype='float32')
    for i, line in enumerate(lines[2:64]):
        data = [float(a) for a in line.split(' ') if a][1:]
        df.iloc[i] = data
    return df


# plot_confusion_matrix(cm, classes=classes)


def print_model(model):
    for layer_num, layer in enumerate(model.layers):
        print(f'Layer number {layer_num}: ', end='')
        if isinstance(layer, Sequential):
            print_model(layer)
        if isinstance(layer, Dense):
            print(f'Dense(units={layer.units}, activation={layer.activation.__name__})')
        elif isinstance(layer, Conv2D):
            print(
                f'Conv2D(filters={layer.filters}, kernel_size={layer.kernel_size},'
                f' activation={layer.activation.__name__}, padding={layer.padding})')
        elif isinstance(layer, MaxPooling2D):
            print(f'MaxPooling2D(pool_size={layer.pool_size}, strides={layer.strides})')
        elif isinstance(layer, Flatten):
            print('Flatten()')
        elif isinstance(layer, Dropout):
            print(f'Dropout({layer.rate})')
        elif isinstance(layer, UpSampling2D):
            print(f'UpSampling2D({layer.size})')


def visualize_model(model, img):
    img_input = Input(shape=(64, 64, 1))
    successive_outputs = [layer.output for layer in model.layers[1:]]
    visualization_model = Model(img_input, successive_outputs)

    img = img.reshape(1, 64, 64, 1)

    successive_feature_maps = visualization_model.predict(img)

    layer_names = [layer.name for layer in model.layers]
    for layer_name, feature_map in zip(layer_names, successive_feature_maps):
        if len(feature_map.shape) == 4:
            # Just do this for the conv / maxpool layers, not the fully-connected layers
            n_features = feature_map.shape[-1]  # number of features in feature map
            # The feature map has shape (1, size, size, n_features)
            size = feature_map.shape[1]
            # We will tile our images in this matrix
            display_grid = np.zeros((size, size * n_features))
            for i in range(n_features):
                # Postprocess the feature to make it visually palatable
                x = feature_map[0, :, :, i]
                x -= x.mean()
                x /= x.std()
                x *= 64
                x += 128
                x = np.clip(x, 0, 255).astype('uint8')
                # We'll tile each filter into this big horizontal grid
                display_grid[:, i * size: (i + 1) * size] = x
            # Display the grid
            scale = 20. / n_features
            plt.figure(figsize=(scale * n_features, scale))
            plt.title(layer_name)
            plt.grid(False)
            plt.imshow(display_grid, aspect='auto')
