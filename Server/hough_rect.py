"""
Module for finding a rectangle in the image, using Hough Line Transform.
"""
import itertools
from typing import Union

import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.spatial import distance

import consts


def find_hough_rect(img: np.ndarray) -> Union[None, np.ndarray]:
    """
    Find the main rectangle in the image using Hough Line Transform. If
    a rectangle is found, returning the ordered four points that define
    the rectangle, else returning None.
    """
    img = cv2.GaussianBlur(img, (7, 7), 0)
    edged = cv2.Canny(img, 50, 250, apertureSize=3)

    lines = cv2.HoughLinesP(edged, rho=1, theta=np.pi / 180, threshold=150,
                            minLineLength=img.shape[0] // 10,
                            maxLineGap=img.shape[0] // 10)
    if lines is None:
        return None
    lines = lines.reshape((len(lines), 4))  # remove unnecessary dimension
    # sort lines by their lengths, from longest to shortest
    lines = sorted(lines,
                   key=lambda l: distance.euclidean((l[0], l[1]), (l[2], l[3])),
                   reverse=True)
    longest_lines = lines[:10]  # take the longest lines
    # debug_show_lines(longest_lines, img.shape)
    pts = get_lines_intersect(longest_lines, img.shape[1], img.shape[0])
    if pts is None:
        # hasn't managed to find four points of intersection
        return None
    return order_points(np.array(pts))


def get_lines_intersect(lines: list, img_width: int,
                        img_height: int) -> Union[None, list[tuple[int, int]]]:
    """
    Get the intersection points of the lines, only if there are exactly
    four of them. Reduce mistakes by filtering close points and unwanted
    points of intersection.
    """
    # get the line equation for each of the lines
    line_equations = [get_line_equation(*line) for line in lines]

    pts = set()
    # get combination of two lines at a time
    for (m1, b1), (m2, b2) in itertools.combinations(line_equations, 2):
        if pt := get_intersection_point(m1, b1, m2, b2, img_width, img_height):
            pts.add(pt)
    pts = filter_close_pts(list(pts), min_pts_dst=img_width // 10)

    if len(pts) != 4:
        return None
    return pts


def get_intersection_point(m1: float, b1: float, m2: float, b2: float,
                           img_width: int, img_height: int) \
        -> Union[None, tuple[int, int]]:
    """
    Get the intersection points of two lines. If the point-of-intersection
    is out of bounds or the angle between the two lines is too small,
    returning None. Otherwise, returning the point.
    """
    if m1 == m2:
        # slopes equal, lines will never meet
        return None
    # if either line is vertical, get the x from the vertical line,
    # and the y from the other line
    if m1 == consts.INFINITY:
        x = b1
        y = m2 * x + b2
    elif m2 == consts.INFINITY:
        x = b2
        y = m1 * x + b1
    else:
        x = (b2 - b1) / (m1 - m2)  # equation achieved by solving m1*x+b1 = m2*x+b2
        y = m1 * x + b1
    if x < 0 or x > img_width - 1 or y < 0 or y > img_height - 1:
        # point-of-intersection out of bounds
        return None

    # obtain the angle between the two lines
    if m1 * m2 == -1:
        alpha = np.pi / 2  # lines are perpendicular, cannot divide by zero
    else:
        alpha = np.arctan(np.abs((m1 - m2) / (1 + m1 * m2)))
    if alpha < np.pi / 16:
        # if the angle is too small, then the two lines are almost
        # parallel, discard point of intersection
        return None
    return int(x), int(y)


def filter_close_pts(pts: list[tuple[int, int]],
                     min_pts_dst: int = 100) -> list[tuple[int, int]]:
    """
    Remove points that are too close one another (usually caused by
    duplicate lines or lines very close to each other).
    """
    filtered_pts = pts[:]

    for i, pt1 in enumerate(pts):
        for j, pt2 in enumerate(pts[i + 1:]):
            if distance.euclidean(pt1, pt2) < min_pts_dst and pt2 in filtered_pts:
                filtered_pts.remove(pt2)

    return filtered_pts


def get_line_equation(x1, y1, x2, y2) -> tuple[float, float]:
    """
    Get line equation (of the form y=mx+b), defined by two points.
    Returning the slope and b. If the two dots are on the same vertical
    line, then the line passing between them cannot be represented
    by the equation y=mx+b, therefore in that case returning 'infinite'
    slope and the x value of the vertical line.
    """
    if x1 == x2:
        return consts.INFINITY, x1  # can't divide by zero, returning 'infinite' slope instead
    m = (y2 - y1) / (x2 - x1)  # slope = dy / dx
    b = -m * x1 + y1  # derived from y=mx+b
    return m, b


def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Order the points of the rectangle according to the following
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


def rect_area(ordered_pts: np.ndarray) -> float:
    """Calculate the area of the quadrilateral defined by the ordered points."""
    # get x and y in vectors
    x, y = zip(*ordered_pts)
    # shift coordinates
    x_ = x - np.mean(x)
    y_ = y - np.mean(y)
    # calculate area
    correction = x_[-1] * y_[0] - y_[-1] * x_[0]
    main_area = np.dot(x_[:-1], y_[1:]) - np.dot(y_[:-1], x_[1:])
    return 0.5 * np.abs(main_area + correction)

# ----------- FOR DEBUGGING -----------


def debug_show_lines(lines, img_shape):
    temp = np.ones(img_shape) * 255
    for line in lines:
        x1, y1, x2, y2 = line
        pt1, pt2 = debug_extend_line(x1, y1, x2, y2, img_shape[1], img_shape[0])
        cv2.line(temp, pt1, pt2, 0, 7)
    plt.imshow(temp)
    plt.show()


def debug_extend_line(x1, y1, x2, y2, img_width, img_height):
    if x1 == x2:
        return (x1, 0), (x1, img_height)
    m = (y2 - y1) / (x2 - x1)
    b = -m * x1 + y1  # derived from y-y1 = m(x-x1)
    f = lambda x: m * x + b
    if b < 0:
        pt1 = (int(-b // m), 0)
    elif b > img_height:
        pt1 = (int((img_height - b) // m), img_height - 1)
    else:
        pt1 = (0, int(f(0)))

    if f(img_width) > img_height:
        pt2 = (int((img_height - b) // m), img_height - 1)
    elif f(img_width) < 0:
        pt2 = (int(-b // m), 0)
    else:
        pt2 = (img_width, int(f(img_width)))

    return pt1, pt2
