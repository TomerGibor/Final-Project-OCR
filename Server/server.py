import base64
import io
from typing import Dict

import numpy as np
import PIL.Image
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# from ocr import text_from_image

app = FastAPI()


class Data(BaseModel):
    b64image: str
    preprocessing: bool

i = 0

@app.post('/convert')
async def predict_text(data: Data) -> Dict[str, str]:
    global i
    base64_decoded = base64.b64decode(data.b64image)
    pil_image = PIL.Image.open(io.BytesIO(base64_decoded)).convert('L')
    pil_image.save('17-11-2020.png')
    print(data.preprocessing)

    # print(image.b64image)
    i += 1
    return {'result': f'test{i}'}
    # pil_image = PIL.Image.open(io.BytesIO(base64_decoded)).convert('L')
    #
    # np_image = np.asarray(pil_image)
    #
    # text = text_from_image(np_image)
    #
    # return {'prediction': text}  # fastapi auto converts dict into JSON


if __name__ == '__main__':
    uvicorn.run('server:app', host='0.0.0.0', port=8080)
