"""
Module for preprocessing the images, in order the get them to work best
with the character-cutting and the models.
"""
from typing import Tuple

import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.spatial import distance
from PIL import Image, ImageOps

from hough_rect import find_hough_rect, rect_area

plt.set_cmap('gray')


def preprocess_image(img: np.ndarray) -> np.ndarray:
    """
    Perform preprocessing on the input image. Try to find corners of the
    page and transform the image to enlarge and rotate the region-of-interest.
    If none is found, only do light preprocessing.

    Args:
        img (np.ndarray): The original image which needs to be processed.
    Returns:
        np.ndarray: The preprocessed image.
    """
    original = img.copy()

    if (roi := find_hough_rect(img)) is None \
            or rect_area(roi) < 0.1 * img.shape[0] * img.shape[1]:
        # can't process image, no ROI found or rect is too small, return
        # original image, after being light preprocessed
        return light_preprocessing(original)

    # rotate the image and transform it around the ROI
    warped = four_point_transform(original, roi)

    # final steps of preprocessing - threshing and eroding
    _, threshed = cv2.threshold(warped, 255 // 2, 255, cv2.THRESH_OTSU)
    eroded = cv2.erode(threshed, np.ones((2, 2)), iterations=2)
    plt.imshow(eroded)
    plt.show()
    return eroded


def four_point_transform(img: np.ndarray, rect: np.ndarray) -> np.ndarray:
    """Warp the image around it's region-of-interest."""
    # obtain a consistent order of the points
    width, height = calc_dimensions(rect)

    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]], dtype=np.float32)

    # compute the perspective transform matrix and then apply it
    matrix = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, matrix, (width, height))
    return warped


def calc_dimensions(ordered_pts: np.ndarray) -> Tuple[int, int]:
    """Calculate the dimensions of the new warped image - width and height."""

    (tl, tr, br, bl) = ordered_pts

    # compute the width of the new image - the maximum distance between
    # right and left points
    width1 = distance.euclidean(br, bl)
    width2 = distance.euclidean(tr, tl)
    max_width = max(int(width1), int(width2))

    # compute the height of the new image - the maximum distance between
    # top and bottom points
    height1 = distance.euclidean(tr, br)
    height2 = distance.euclidean(tl, bl)
    max_height = max(int(height1), int(height2))

    return max_width, max_height


def light_preprocessing(img: np.ndarray) -> np.ndarray:
    """Perform light preprocessing of the image. Do only thresholding."""
    _, threshed = cv2.threshold(img, 255 // 2, 255, cv2.THRESH_OTSU)
    return threshed


# image = Image.open('tests/preprocessing/test2.png').convert('L')
# image = np.asarray(ImageOps.exif_transpose(image))
#
# preprocess_image(image)
