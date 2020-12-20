"""
Module for running the server that communicated with the clients and
answers their requests.
"""
import base64
import io
import os
import binascii
from typing import Dict

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
from preprocessing import preprocess_image, light_preprocessing

app = FastAPI()


class Data(BaseModel):
    b64image: str
    preprocessing: bool


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
async def invalid_b64_str_handler(request: Request,
                                  exc: InvalidImageStringError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={'message': 'Cannot identify image file from decoded base64 string.'},
    )


@app.post('/image_to_text')
async def image_to_text(data: Data) -> Dict[str, str]:
    """Extract the text from an image, and preprocess it if requested."""
    try:
        base64_decoded = base64.b64decode(data.b64image)
    except binascii.Error:
        raise InvalidBase64StringError()
    try:
        pil_image = Image.open(io.BytesIO(base64_decoded)).convert('L')
    except UnidentifiedImageError:
        raise InvalidImageStringError()

    pil_image = ImageOps.exif_transpose(pil_image)
    np_image = np.asarray(pil_image)

    if data.preprocessing:
        preprocessed = preprocess_image(np_image)
    else:
        preprocessed = light_preprocessing(np_image)

    text = text_from_image(preprocessed)
    return {'result': text}


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
