import string
from collections import namedtuple
from typing import Tuple, List
from numbers import Real

import PIL
import cv2
import numpy as np
import matplotlib.pyplot as plt
from spellchecker import SpellChecker

import consts
from ocr_model import OCRModel
from noise_remover import DenoisingAutoencoder

# load the models
model = OCRModel()
denoiser = DenoisingAutoencoder()
model.load_model()
denoiser.load_model()

# set color palette to gray
plt.set_cmap('gray')
# define namedtuple to hold rectangle information
Rect = namedtuple('Rect', 'x y w h')
PADDING = 16
spellchecker = SpellChecker()
common_mistakes = {
    'ls': 'is',
    'lt': 'it',
    'l': 'i',
}


def get_median_dimensions(rects: List[Rect]) -> Tuple[Real, Real]:
    """Get the 3/4 median of the dimensions."""
    heights = [rect.h for rect in rects]
    widths = [rect.w for rect in rects]

    heights.sort()
    widths.sort()

    median_height = heights[int(3 * len(heights) / 4)]
    median_width = widths[int(3 * len(widths) / 4)]

    return median_width, median_height


def filter_contour_rects(contour_rects: List[Tuple[np.ndarray, Rect]],
                         median_area: Real) -> List[Tuple[np.ndarray, Rect]]:
    """
    Remove tiny or big rects and their matching contours,
    based on the median area.
    """

    filtered_contour_rects = []

    for contour, rect in contour_rects:
        if rect.w * rect.h < 0.2 * median_area:
            # discard small rects and contours
            continue
        if rect.w * rect.h > 5 * median_area:
            # discard large rects and contours
            continue
        filtered_contour_rects.append((contour, rect))
    return filtered_contour_rects


def sort_rects(contour_rects: List[Tuple[np.ndarray, Rect]],
               median_height: Real) -> List[Tuple[np.ndarray, Rect]]:
    """
    Sort the contours and rects together, by forming liens of characters based
    on change in vertical distance between two characters. After forming lines,
    sort each line by the x position of its rects.
    """
    # firstly, sort the contours by their rect's y position
    sorted_by_y = sorted(contour_rects, key=lambda cr: cr[1].y)

    line, sorted_contour_rects = [], []
    # function to calculate vertical distance between two rects
    vertical_dist = lambda r1, r2: r2.y - (r1.y + r1.h)

    # loop over the contour rects in pairs
    for (contour1, rect1), (contour2, rect2) in zip(sorted_by_y[:-1], sorted_by_y[1:]):
        line.append((contour1, rect1))
        if vertical_dist(rect1, rect2) > median_height / 2:
            # reached new line, sort current line by x position, and add
            # to sorted contour rects
            sorted_contour_rects += sorted(line, key=lambda cr: cr[1].x)
            line = [(contour2, rect2)]
    if len(sorted_by_y) > 1:
        line.append((contour2, rect2))

    # add last line of text, and return the sorted rects and contours
    sorted_contour_rects += sorted(line, key=lambda cr: cr[1].x)
    return sorted_contour_rects


def detect_spaces(contour_rects: List[Tuple[np.ndarray, Rect]],
                  median_width: Real) -> List[Tuple[np.ndarray, Rect]]:
    """
    Detect spaces between sorted contours, by measuring the horizontal
    distance between adjacent contours, and comparing it to the median width.
    """
    with_spaces = []
    horizontal_distance = lambda r1, r2: r2.x - (r1.x + r1.w)
    for (contour1, rect1), (contour2, rect2) in zip(contour_rects[:-1], contour_rects[1:]):
        with_spaces.append((contour1, rect1))
        if horizontal_distance(rect1, rect2) > median_width / 2 \
                or horizontal_distance(rect1, rect2) < -3 * median_width:
            with_spaces.append(('SPACE', 'SPACE'))
    with_spaces.append((contour2, rect2))
    return with_spaces


def remove_enclosing_rects(contour_rects: List[Tuple[np.ndarray, Rect]]) \
        -> List[Tuple[np.ndarray, Rect]]:
    """
    Remove rects and their corresponding contours, if one rect is enclosed
    by another. Always removing the enclosed ones.
    """
    filtered = []
    skip = False
    # function to determine if two one rect encloses the other
    is_enclosing = lambda r1, r2: r2.x + r2.w < r1.x + r1.w and r2.y + r2.h < r1.y + r1.h
    # loop over the contour rects in pairs
    for (contour1, rect1), (contour2, rect2) in zip(contour_rects[:-1], contour_rects[1:]):
        if is_enclosing(rect1, rect2):
            # if enclosing, only keep the bigger one
            filtered.append((contour1, rect1))
            skip = True
            continue
        elif not skip:
            # if not enclosing, keep contour
            filtered.append((contour1, rect1))
        skip = False
    if not skip:
        filtered.append((contour2, rect2))

    return filtered


def text_from_image(img: np.ndarray) -> str:
    """Extract the text from an image."""
    original = img.copy()
    # convert to only black and white
    _, img = cv2.threshold(img, 150, 255, cv2.THRESH_OTSU)
    plt.imshow(original)
    plt.show()

    rect_kernel = np.ones((2, 2))

    erosion = cv2.erode(img, rect_kernel, iterations=1)

    contours, _ = cv2.findContours(erosion, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    # get the bounding rects of the contours
    rects = [Rect(*cv2.boundingRect(cnt)) for cnt in contours]

    median_width, median_height = get_median_dimensions(rects)
    contour_rects = list(zip(contours, rects))
    contour_rects = filter_contour_rects(contour_rects, median_width * median_height)
    contour_rects = sort_rects(contour_rects, median_height)
    contour_rects = remove_enclosing_rects(contour_rects)
    # show_rects(original, rects)
    with_spaces = detect_spaces(contour_rects, median_width)

    # unpack contours and rects
    contours, rects = zip(*with_spaces)
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
        character = original[rect.y:rect.y + rect.h, rect.x:rect.x + rect.w]
        character = add_padding(character)

        # resize the image to be the size defined in consts, and rescale
        # pixel values to be between 0.0 and 1.0
        scaled = cv2.resize(character, consts.IMAGE_SIZE) / 255

        denoised = denoiser.denoise_image(scaled)
        plt.imshow(denoised)
        plt.show()
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


# def show_rects(img, rects):
#     for rect in rects:
#         letter = img[rect.y:rect.y + rect.h, rect.x:rect.x + rect.w]
#         letter = add_padding(letter)
#
#         # resize the image to be the size defined in consts, and rescale
#         # pixel values to be between 0.0 and 1.0
#         scaled = cv2.resize(letter, consts.IMAGE_SIZE) / 255
#         denoised = denoiser.denoise_image(scaled)
#         plt.imshow(denoised)
#         plt.show()
#
#
# image = np.asarray(PIL.Image.open('tests\\test9.png').convert('L'))
#
# text_from_image(image)
