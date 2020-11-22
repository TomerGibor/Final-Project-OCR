import base64
import io
from datetime import datetime
from typing import Dict

import numpy as np
import PIL.Image
import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from docx import Document
from docx.shared import Pt

# from ocr import text_from_image

app = FastAPI()


class Data(BaseModel):
    b64image: str
    preprocessing: bool


i = 0


@app.post('/image_to_text')
async def image_to_text(data: Data) -> Dict[str, str]:
    global i
    base64_decoded = base64.b64decode(data.b64image)
    pil_image = PIL.Image.open(io.BytesIO(base64_decoded)).convert('L')
    pil_image.save(f'{datetime.now().strftime("%Y-%b-%dT%H-%m-%S")}.png')
    print(data.preprocessing)

    # print(image.b64image)
    i += 1
    return {'result': f'test{i}'}

    # np_image = np.asarray(pil_image)
    #
    # text = text_from_image(np_image)
    #
    # return {'prediction': text}  # fastapi auto converts dict into JSON


@app.get('/text_to_docx/{text}')
async def text_to_docx(text: str):
    document = Document()
    paragraph = document.add_paragraph(text)
    style = document.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(12)
    paragraph.style = document.styles['Normal']

    stream = io.BytesIO()
    document.save(stream)
    return Response(content=stream.getvalue(), media_type='application/vnd.openxmlformats'
                                                          '-officedocument.wordprocessingml.document')


if __name__ == '__main__':
    uvicorn.run('server:app', host='0.0.0.0', port=8080)
