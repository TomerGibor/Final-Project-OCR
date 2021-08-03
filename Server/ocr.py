"""
Module for extracting the text from an image using optical-character-recognition.
"""
import string

import cv2
import numpy as np
from spellchecker import SpellChecker

import consts
from ocr_model import OCRModel
from noise_remover import DenoisingAutoencoder
from bounding_rects import get_letters_bounding_rects_as_words, Rect

# load the models
model = OCRModel()
denoiser = DenoisingAutoencoder()
model.load_model()
denoiser.load_model()

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

    words = get_letters_bounding_rects_as_words(img)
    text = ' '.join([characters_from_word(img, word) for word in words])
    print(f'Before spellchecking: {text}')
    return perform_spellchecking(text)


def characters_from_word(img: np.ndarray, word: list[Rect]) -> str:
    """Predict the word one letter at a time. Cut rect from image, add
    padding, resize, de-noise, and predict."""
    first_character_of_word = True
    is_word_letters = True  # whether the word starts with a letter or a number
    text = ''
    for rect in word:
        char = prepare_character_for_prediction(img, rect)
        # predict the character
        prediction = model.predict(char)
        predicted_letter = consts.CLASSES[np.argmax(prediction)]

        if first_character_of_word and predicted_letter in string.digits:
            is_word_letters = False
        predicted_letter = change_to_similar_character_if_needed(
            predicted_letter, first_character_of_word, is_word_letters
        )

        text += predicted_letter
        first_character_of_word = False
    return text


def prepare_character_for_prediction(img: np.ndarray, rect: Rect) -> np.ndarray:
    """Cut the character from the image according to the given rect,
    add padding and scale the image appropriately."""
    # crop the bounding rect of the character from the original image
    character = img[rect.y:rect.y + rect.h, rect.x:rect.x + rect.w]
    # add white padding around the character and center it in the frame
    character = add_padding(character)
    # resize the image, and rescale pixel values to be between 0.0 and 1.0
    scaled = cv2.resize(character, consts.IMAGE_SIZE) / 255
    denoised = denoiser.denoise_image(scaled)
    return denoised


def add_padding(img: np.ndarray) -> np.ndarray:
    """Add white space padding to make the image a square, and add
    padding around the image.
    """
    height, width = img.shape
    max_dim = max(width, height)
    pad = int(max_dim * consts.CHARACTER_PADDING_RATIO)
    padded = np.ones((max_dim + 2 * pad, max_dim + 2 * pad)) * 255
    # calculate the x and y offsets
    x_start = (max_dim - width) // 2 + pad
    y_start = (max_dim - height) // 2 + pad
    # reposition original image at the center of the new image, with white padding
    # on the sides
    padded[y_start:y_start + height, x_start:x_start + width] = img
    return padded


def change_to_similar_character_if_needed(predicted_letter: str,
                                          first_character_of_word: bool,
                                          is_word_letters: bool) -> str:
    """
    Alter the predicted character to a character that looks similar, from
    numbers to letters. In case the character is a number positioned in
    the middle of a word, replace it with a letter that is visually
    similar (the model is inaccurate at times).
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
    corrected_words = [spellchecker.correction(word) for word in words]
    print(f'After spellchecking: {" ".join(corrected_words)}')
    return ' '.join(corrected_words)
