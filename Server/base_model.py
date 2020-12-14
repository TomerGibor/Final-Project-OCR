"""Module used to define the base model and other related functions and errors."""
from abc import ABCMeta, abstractmethod
from functools import wraps

from tensorflow.keras.models import Sequential


class ABCSingletonMeta(ABCMeta):
    """An implementation of abstract base class and singleton using metaclass."""
    __instances = {}

    def __call__(cls, *args, **kwargs):
        """Custom creation of instance."""
        return cls.__instances.setdefault(cls.__name__,
                                          type.__call__(cls, *args, **kwargs))


class BaseTFModel(metaclass=ABCSingletonMeta):
    """
    An abstract class that defines the required functions for TF model.
    Every class that inherits from this class, will be a singleton itself.
    """

    def __init__(self):
        self._model: Sequential = None
        self._model_loaded = False
        self._model_built = False

    @abstractmethod
    def build_model(self):
        ...

    @abstractmethod
    def train_model(self):
        ...

    @abstractmethod
    def load_model(self):
        ...

    @abstractmethod
    def save_model(self):
        ...

    @abstractmethod
    def evaluate(self, images):
        ...


class ModelError(Exception):
    """Base model exception"""


class ModelNotLoadedError(ModelError):
    """Exception raised when trying to predict on an unloaded model."""


class ModelNotBuiltError(ModelError):
    """Exception raised when trying to train an un built model."""


def singleton(cls):
    """ An implementation of singleton using decorator. """
    _instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        return _instances.setdefault(cls.__name__, cls(*args, **kwargs))

    return wrapper
