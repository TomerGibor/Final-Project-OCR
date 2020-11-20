import string

import PIL
import cv2
import numpy as np
import matplotlib.pyplot as plt
from spellchecker import SpellChecker

import consts
from ocr_model import OCRModel
from noise_remover import DenoisingAutoencoder
from cv import get_contours_bounding_rects

# load the models
model = OCRModel()
denoiser = DenoisingAutoencoder()
model.load_model()
denoiser.load_model()

# set color palette to gray
plt.set_cmap('gray')
PADDING = 16
spellchecker = SpellChecker()
common_mistakes = {
    'ls': 'is',
    'lt': 'it',
    'l': 'i',
}


def text_from_image(img: np.ndarray) -> str:
    """Extract the text from an image."""

    rects = get_contours_bounding_rects(img)
    text = ''
    first_character_of_word = True
    is_word_letters = True
    for rect in rects:
        if rect == 'SPACE':
            text += ' '
            first_character_of_word = True
            is_word_letters = True
            continue
        # crop the bounding rect of the contour from the original image
        character = img[rect.y:rect.y + rect.h, rect.x:rect.x + rect.w]
        character = add_padding(character)

        # resize the image to be the size defined in consts, and rescale
        # pixel values to be between 0.0 and 1.0
        scaled = cv2.resize(character, consts.IMAGE_SIZE) / 255

        denoised = denoiser.denoise_image(scaled)
        # plt.imshow(denoised)
        # plt.show()
        prediction = model.predict(denoised)
        predicted_letter = consts.MERGED_CLASSES[np.argmax(prediction)]
        if first_character_of_word and predicted_letter in string.digits:
            is_word_letters = False
        if not first_character_of_word:
            if is_word_letters and predicted_letter == '0':
                predicted_letter = 'o'
            elif is_word_letters and predicted_letter == '1':
                # TODO: i or l
                predicted_letter = 'i'
        if not is_word_letters:
            if predicted_letter == 'z':
                predicted_letter = '2'
            if predicted_letter == 'i' or predicted_letter == 'l':
                predicted_letter = '1'
        text += predicted_letter
        first_character_of_word = False
    words = text.split(' ')
    words = [common_mistakes.get(word, word) for word in words]
    corrected_words = []
    for word in words:
        corrected_words.append(spellchecker.correction(word))
    print(' '.join(corrected_words))
    return ' '.join(corrected_words)


def add_padding(img):
    """Add white space padding to make the image a square."""
    width, height = img.shape
    max_dim = max(width, height)

    temp = np.ones((max_dim, max_dim)) * 255
    # calculate the x and y offsets
    x_offset = (max_dim - width) // 2
    y_offset = (max_dim - height) // 2
    # reposition original image at the center of the new image, with white padding
    # on the sides
    temp[x_offset:x_offset + width, y_offset:y_offset + height] = img

    # add extra padding from all sides so that the image will not touch
    # the edge of the array frame
    return np.pad(temp, PADDING, constant_values=255)


image = np.asarray(PIL.Image.open('tests\\test9.png').convert('L'))

text_from_image(image)
