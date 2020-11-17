import string

IMAGE_SIZE = (64, 64)
TRAIN_ALL_PATH = 'D:\\Training Data\\Training Dataset\\training_all'
VALIDATION_ALL_PATH = 'D:\\Training Data\\Training Dataset\\validation_all'
HEX_CLASSES = [format(ord(c), 'x') for c in string.ascii_letters + string.digits]
CHARACTERS = string.ascii_letters + string.digits
MERGED_CHARACTERS = string.ascii_lowercase + string.digits
MERGED_CLASSES = string.ascii_lowercase + string.digits
TRAIN_PATH = 'D:\\Training Data\\Training Dataset\\non_filtered_training_2'
VALIDATION_PATH = 'D:\\Training Data\\Training Dataset\\non_filtered_validation'
TRAIN_MERGED_PATH = 'D:\\Training Data\\Training Dataset\\non_filtered_training_merged'
VALIDATION_MERGED_PATH = 'D:\\Training Data\\Training Dataset\\non_filtered_validation_merged'
DATETIME_FORMAT = '%d-%b-%Y-%H%M'
