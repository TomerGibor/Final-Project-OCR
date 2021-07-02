"""
Module for running the server that communicated with the clients and
answers their requests.
"""
import base64
import io
import os
import binascii
from typing import Optional

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from docx import Document
from docx.shared import Pt

import consts
from ocr import text_from_image
from preprocessing import preprocess_image, find_page_points

app = FastAPI()


class Data(BaseModel):
    b64image: str
    points: Optional[list[dict[str, int]]]


class InvalidBase64StringError(Exception):
    """Exception raised if base64 decoding failed."""


class InvalidImageStringError(Exception):
    """Exception raised when an image file cannot be identified from decoded base64."""


@app.exception_handler(InvalidBase64StringError)
async def invalid_b64_str_handler(request: Request,
                                  exc: InvalidBase64StringError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={'message': 'The received base64 string is invalid.'},
    )


@app.exception_handler(InvalidImageStringError)
async def invalid_b64_img_handler(request: Request,
                                  exc: InvalidImageStringError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={'message': 'Cannot identify image file from decoded base64 string.'},
    )


def decode_image(b64image: str) -> np.ndarray:
    """Try decoding the image from base64 string, into numpy array."""
    try:
        base64_decoded = base64.b64decode(b64image)
    except binascii.Error:
        raise InvalidBase64StringError()
    try:
        pil_image = Image.open(io.BytesIO(base64_decoded)).convert('L')
    except UnidentifiedImageError:
        raise InvalidImageStringError()

    pil_image = ImageOps.exif_transpose(pil_image)
    np_image = np.asarray(pil_image)
    return np_image


@app.post('/image_to_text')
async def image_to_text(data: Data) -> dict[str, str]:
    """Extract the text from an image, and preprocess it using the received points."""
    np_image = decode_image(data.b64image)

    if data.points:
        points = [(pt['x'], pt['y']) for pt in data.points]
    else:
        points = None
    preprocessed = preprocess_image(np_image, points)

    text = text_from_image(preprocessed)
    return {'result': text}


@app.post('/find_page_points')
async def find_points(data: Data) -> dict[str, list[dict[str, int]]]:
    """Find the points of the region-of-interest in the image."""
    np_image = decode_image(data.b64image)
    points = find_page_points(np_image)
    return {'points': [{'x': int(pt[0]), 'y': int(pt[1])} for pt in points]}


@app.get('/text_to_docx/{text}')
async def text_to_docx(text: str):
    """Put the text in a docx document."""
    document = Document()
    paragraph = document.add_paragraph(text)
    style = document.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(12)
    paragraph.style = document.styles['Normal']

    stream = io.BytesIO()
    document.save(stream)
    return Response(content=stream.getvalue(),
                    media_type=consts.DOCX_MIME_TYPE)


if __name__ == '__main__':
    uvicorn.run('server:app', host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
