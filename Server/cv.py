from collections import namedtuple
from typing import Tuple, List
from numbers import Real

import numpy as np
import cv2
import matplotlib.pyplot as plt

# set color palette to gray
plt.set_cmap('gray')
Rect = namedtuple('Rect', 'x y w h')


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


def get_contours_bounding_rects(img: np.ndarray) -> List[Rect]:
    img = img.copy()  # np arrays are mutable and are passed by reference
    # convert to only black and white
    _, img = cv2.threshold(img, 150, 255, cv2.THRESH_OTSU)
    plt.imshow(img)
    plt.show()

    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
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

    return rects

# def show_rects(img, rects):
#     for rect in rects:
#         letter = img[rect.y:rect.y + rect.h, rect.x:rect.x + rect.w]
#         letter = add_padding(letter)
#
#         # resize the image to be the size defined in consts, and rescale
#         # pixel values to be between 0.0 and 1.0
#         scaled = cv2.resize(letter, consts.IMAGE_SIZE) / 255
#         plt.imshow(denoised)
#         plt.show()
