"""Module for defining application-level constants."""
import string

IMAGE_SIZE = (64, 64)
TRAIN_NON_CATEGORICAL_PATH = 'C:\\Training Dataset\\training_all'
VALIDATION_NON_CATEGORICAL_PATH = 'C:\\Training Dataset\\validation_all'
CLASSES = [c for c in string.ascii_lowercase + string.digits]
TRAIN_CATEGORICAL_PATH = 'C:\\Training Dataset\\non_filtered_training_merged'
VALIDATION_CATEGORICAL_PATH = 'C:\\Training Dataset\\non_filtered_validation_merged'
TEST_CATEGORICAL_PATH = 'C:\\Training Dataset\\non_filtered_test_merged'
DATETIME_FORMAT = '%d-%b-%Y-%H%M'
DOCX_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
CHARACTER_PADDING_RATIO = 0.25
SPACE = 'SPACE'
INFINITY = 2**64
EVALUATION_RESULTS_DIR = '.\\evaluation_results'
