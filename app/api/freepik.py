from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import FREEPIK_API_KEY
import requests

router = APIRouter()

# Definir un modelo de datos para validar el prompt
class PromptRequest(BaseModel):
    prompt: str

@router.post("/freepik/generate_image")
def generate_image_from_prompt(data: PromptRequest):
    prompt = data.prompt
    print("Dentro de la función para generar la imagen")
    print(f"Prompt: {prompt}")
    print(f"API Key: {FREEPIK_API_KEY}")

    url = "https://api.freepik.com/v1/ai/text-to-image"
    headers = {
        "x-freepik-api-key": FREEPIK_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "styling": {
            "style": "photo",
            "color": "vibrant",
            "lightning": "studio",
            "framing": "aerial-view"
        },
        "image": {"size": "square_1_1"}
    }

    # Realizar la solicitud a la API de Freepik
    response = requests.post(url, json=payload, headers=headers)

    # Procesar la respuesta de la API
    if response.status_code == 200:
        try:
            image_base64 = response.json()["data"][0]["base64"]
            return {"message": "Imagen generada correctamente", "image_base64": image_base64}
        except (KeyError, IndexError, TypeError):
            raise HTTPException(
                status_code=500, detail="Error al obtener la imagen generada en formato base64"
            )
    else:
        error_message = response.json().get("error", "Error desconocido al generar la imagen")
        raise HTTPException(status_code=response.status_code, detail=f"Error en Freepik API: {error_message}")
