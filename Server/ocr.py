"""
Module for extracting the text from an image using optical-character-recognition.
"""
import string

import PIL
import cv2
import numpy as np
import matplotlib.pyplot as plt
from spellchecker import SpellChecker

import consts
from ocr_model import OCRModel
from noise_remover import DenoisingAutoencoder
from cv import get_letters_bounding_rects

# load the models
model = OCRModel()
denoiser = DenoisingAutoencoder()
model.load_model()
denoiser.load_model()

# set color palette to gray
plt.set_cmap('gray')
spellchecker = SpellChecker()
common_mistakes = {
    'ls': 'is',
    'lt': 'it',
    'l': 'i',
    'ln': 'in',
    'lts': 'its',
    'll': 'it',
}


def text_from_image(img: np.ndarray) -> str:
    """
    Extract the text from an image. Works best if the image is preprocessed
    before applying the model.

    Args:
        img (np.ndarray): The image (preprocessed).

    Returns:
        str: The extracted text.
    """

    rects = get_letters_bounding_rects(img)

    text = ''
    first_character_of_word = True
    is_word_letters = True  # whether the word starts with a letter or a number

    for rect in rects:
        if rect == consts.SPACE:
            text += ' '
            first_character_of_word = True
            is_word_letters = True
            continue

        # crop the bounding rect of the contour from the original image
        character = img[rect.y:rect.y + rect.h, rect.x:rect.x + rect.w]
        # add white padding around the character and center it in the frame
        character = add_padding(character)

        # resize the image, and rescale pixel values to be between 0.0 and 1.0
        scaled = cv2.resize(character, consts.IMAGE_SIZE) / 255

        denoised = denoiser.denoise_image(scaled)

        # predict the character
        prediction = model.predict(denoised)
        predicted_letter = consts.CLASSES[np.argmax(prediction)]

        if first_character_of_word and predicted_letter in string.digits:
            is_word_letters = False
        predicted_letter = change_to_similar_character_if_needed(
            predicted_letter, first_character_of_word, is_word_letters
        )

        text += predicted_letter
        first_character_of_word = False

    return perform_spellchecking(text)


def add_padding(img: np.ndarray) -> np.ndarray:
    """Add white space padding to make the image a square, and add
    padding around the image.
    """
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
    return np.pad(temp, consts.CHARACTER_PADDING, constant_values=255)


def change_to_similar_character_if_needed(predicted_letter: str,
                                          first_character_of_word: bool,
                                          is_word_letters: bool) -> str:
    """
    Alter the predicted character to a character that looks similar, from
    letters to numbers or the other way around. In case the character is
    positioned in the middle of a word, replace it with a number that is
    visually similar (the model is inaccurate at times), or if we're at
    the middle of a number, replace the letter with a number.
    """
    if not first_character_of_word and is_word_letters:
        # the word is made of letters
        if predicted_letter == '0':
            predicted_letter = 'o'
        elif predicted_letter == '1':
            predicted_letter = 'i'
        elif predicted_letter == '2':
            predicted_letter = 'z'
        elif predicted_letter == '5':
            predicted_letter = 's'

    return predicted_letter


def perform_spellchecking(text: str) -> str:
    """
    Fix spelling error which may be caused by the model predicting
    the wrong character, by replacing misspelled words, with other words
    which are lexicographically close, and are used often.
    """
    words = text.split(' ')
    words = [common_mistakes.get(word, word) for word in words]
    corrected_words = []
    for word in words:
        corrected_words.append(spellchecker.correction(word))
    print(' '.join(corrected_words))
    return ' '.join(corrected_words)
