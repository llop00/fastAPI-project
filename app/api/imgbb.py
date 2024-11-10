from fastapi import APIRouter
from app.core.config import IMGBB_API_KEY
import requests
import base64

router = APIRouter()

@router.post("/imgbb/upload")
def upload_image(image_bytes: bytes):
    url = 'https://api.imgbb.com/1/upload'
    payload = {
        'key': IMGBB_API_KEY,
        'image': base64.b64encode(image_bytes).decode('utf-8'),
        'expiration': 60  # La imagen expira en 60 segundos
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()  # Devolver los detalles, incluyendo la URL pública
    else:
        return {"error": "Error al subir la imagen a IMGBB"}
