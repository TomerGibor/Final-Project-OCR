"""
Module used for getting the letters bounding rects.
"""
from collections import namedtuple

import numpy as np
import cv2
import matplotlib.pyplot as plt

Rect = namedtuple('Rect', 'x y w h')


def get_median_width(rects: list[Rect]) -> float:
    """Get the median of the widths."""
    widths = [rect.w for rect in rects]
    widths.sort()
    median_width = widths[int(len(widths) / 2)]
    return median_width


def divide_into_words(rects: list[Rect]) -> list[list[Rect]]:
    """
    Divide the rects into words, by detecting spaces between rects, which
    is done by measuring the horizontal distance between adjacent rects,
    and comparing it to the median width of a rect.
    """
    median_width = get_median_width(rects)

    if len(rects) <= 1:
        return [rects]
    words, word = [], []
    horizontal_distance = lambda r1, r2: r2.x - (r1.x + r1.w)
    for rect1, rect2 in zip(rects[:-1], rects[1:]):
        word.append(rect1)
        if horizontal_distance(rect1, rect2) > median_width / 1.5 \
                or horizontal_distance(rect1, rect2) < -2 * median_width:
            words.append(word)
            word = []
    words.append(word + [rect2])
    return words


def black_in_row(img: np.ndarray, row: int, from_col: int, to_col: int) -> bool:
    """
    Returns whether there is a black pixel in row `row` from column
    `from_col` to column `to_col`.
    """
    for pix in img[row, from_col:to_col]:
        if pix == 0:
            return True
    return False


def black_in_column(img: np.ndarray, from_row: int, to_row: int, col: int) -> bool:
    """
    Returns whether there is a black pixel in column `col` from row
    `from_row` to row `to_row`.
    """
    for row in range(from_row, to_row):
        if img[row, col] == 0:
            return True
    return False


def get_rows(img: np.ndarray) -> list[tuple[int, int]]:
    """
    Get the borders of the rows in the text.

    Args:
        img (np.ndarray): The source image.

    Returns:
        list[tuple[int, int]]: A list of tuples with two values,
          representing the first index where the row starts, and the
          last index where the row ends.
    """
    rows = []
    h, w = img.shape
    row = 0
    while row < h:
        # skip all of the empty rows
        while row < h and not black_in_row(img, row, 0, w):
            row += 1
        # loop until the row does not have a black pixel in it anymore
        start = row
        while row < h and black_in_row(img, row, 0, w):
            row += 1
        if start != h:
            rows.append((start, row))
    return rows


def rects_from_row(img: np.ndarray, start_row: int, end_row: int) -> list[Rect]:
    """Get a list of the rects enclosing the letters from all sides,
     within a certain row."""
    rects = []
    h, w = img.shape
    col = 0
    while col < w:
        # skip all of the empty columns
        while col < w and not black_in_column(img, start_row, end_row, col):
            col += 1

        # mark the beginning of the letter, and loop until the column does
        # not have a black pixel in it anymore
        start_col = col
        while col < w and black_in_column(img, start_row, end_row, col):
            col += 1

        # find the top and bottom of the letter
        top = start_row
        while top < h and not black_in_row(img, top, start_col, col):
            top += 1
        bottom = end_row - 1
        while bottom > 0 and not black_in_row(img, bottom, start_col, col):
            bottom -= 1

        letter_w = col - start_col
        letter_h = bottom - top
        if start_col != w and letter_w * letter_h > 200:
            rects.append(Rect(start_col, top, letter_w, letter_h))
    return rects


def get_rects_not_seperated(img: np.ndarray) -> list[Rect]:
    """Loop through every row, and obtain all of the rectangles in the row."""
    h, w = img.shape
    rows = get_rows(img)
    rects = []
    for start, end in rows:
        if end - start > 0.05 * h:  # if the row is not tiny (probably noise)
            rects += rects_from_row(img, start, end)
    return rects


def get_letters_bounding_rects_as_words(img: np.ndarray) -> list[list[Rect]]:
    """
    Get the enclosing rects of the letters in the image, in a sorted order,
    as a list of lists of rects.

    Args:
        img (np.ndarray): The source image.

    Returns:
       list[list[Rect]]: A list of words, where a word is a list of the
         bounding rectangles of every character.
    """
    img = img.copy()  # np arrays are mutable and are passed by reference
    # blur the image
    img = cv2.GaussianBlur(img, (3, 3), 0)
    # obtain the enclosing rectangles
    rects = get_rects_not_seperated(img)

    # ---------------- FOR DEBUGGING ---------------
    img2 = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2RGB)
    for i in rects:
        img2 = cv2.rectangle(img2, (i.x, i.y), (i.x + i.w, i.y + i.h), (0, 255, 0), 2)
    plt.imshow(img2)
    plt.show()
    # ----------------------------------------------
    words = divide_into_words(rects)
    return words
