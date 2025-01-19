from fastapi import APIRouter, HTTPException
from app.core.config import IMGBB_API_KEY
import requests
import base64

router = APIRouter()

@router.post("/imgbb/upload")
def upload_image_to_imgbb(base64_image: str, expiration: int = 60) -> dict:
    """
    Sube una imagen en base64 a Imgbb y devuelve tanto la URL pública como la delete_url.
    Lanza HTTPException si falla.
    """
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": base64_image,
        "expiration": expiration
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        try:
            data = response.json()["data"]
            # data["url"] -> enlace directo
            # data["delete_url"] -> enlace para borrarla
            return {
                "url": data["url"],
                "delete_url": data["delete_url"]
            }
        except (KeyError, TypeError):
            raise HTTPException(500, "Error al procesar la respuesta de Imgbb.")
    else:
        raise HTTPException(response.status_code, f"Error al subir la imagen a Imgbb: {response.text}")
