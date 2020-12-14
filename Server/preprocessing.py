"""
Module for preprocessing tha images, in order the get them to work best
with the character-cutting and the models.
"""
from typing import Tuple, List

import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.spatial import distance
from PIL import Image, ImageOps

plt.set_cmap('gray')


def get_roi(contours: List[np.ndarray]) -> np.ndarray:
    """
    Get the region-of-interest from the list of contours. Get the
    largest contours by area, and then check if either one is a rectangle,
    if none of the contours match said description, return None.

    Args:
        contours (List[np.ndarray]): The contours found by openCV.
    Returns:
        np.ndarray: The contour which serves as the region-of-interest of the image.
    """
    # get the 5 contours with the largest area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    roi = None
    # loop over the contours
    for cnt in contours:
        # approximate the contour
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
        # if the approximated contour has four points, then assume it is the
        # desired area of text (ROI)
        if len(approx) == 4:
            roi = approx
            break
    return roi


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

    img = cv2.GaussianBlur(img, (5, 5), 0)
    edged = cv2.Canny(img, 50, 250)
    plt.imshow(edged)
    plt.show()

    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if (roi := get_roi(contours)) is None:
        # can't process image, no ROI found, return original image,
        # after being light preprocessed
        return light_preprocessing(original)

    # rotate the image and transform it around the ROI
    warped = four_point_transform(original, roi.reshape(4, 2))

    # final steps of preprocessing - threshing and eroding
    _, threshed = cv2.threshold(warped, 255 // 2, 255, cv2.THRESH_OTSU)
    eroded = cv2.erode(threshed, np.ones((2, 2)), iterations=2)
    plt.imshow(eroded)
    plt.show()
    return eroded


def order_points(pts):
    """
    Order the points of the region-of-interest according to the following
    order: top-left, top-right, bottom-right, bottom-left.
    """
    # prepare an array to hold the ordered points
    rect = np.zeros((4, 2), dtype=np.float32)

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def four_point_transform(img, pts):
    """Warp the image around it's region-of-interest."""
    # obtain a consistent order of the points
    rect = order_points(pts)
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


def calc_dimensions(ordered_pts) -> Tuple[int, int]:
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

#
# image = Image.open('tests\\test11.png').convert('L')
# image = np.asarray(ImageOps.exif_transpose(image))
#
# preprocess_image(image)
