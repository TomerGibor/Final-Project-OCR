"""Module used to run the evaluation of the OCR model."""
from ocr_model import OCRModel

model = OCRModel()
model.load_model()
model.evaluate()
