from typing import TypeVar, Generic
import numpy as np

Shape = TypeVar("Shape")
DType = TypeVar("DType")


class Array(np.ndarray, Generic[Shape, DType]):
    """
    Use this to type-annotate numpy arrays, e.g.

        def transform_image(image: Array['H,W,3', np.uint8], ...):
            ...

    """



