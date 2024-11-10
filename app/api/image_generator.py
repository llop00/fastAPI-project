from fastapi import APIRouter
from app.core.config import processor, model_blip, pipe, device
from PIL import Image
import torch
import os
from io import BytesIO

router = APIRouter()

@router.post("/ia/generate_image")
def generar_imagen(prompt: str):
    try:
        with torch.no_grad():
            image = pipe(prompt).images[0]
        
        # Guardar la imagen en memoria (BytesIO)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        buffered.seek(0)
        
        # Retornar la imagen en bytes
        return {"message": "Imagen generada correctamente", "image_bytes": buffered.getvalue()}
    except Exception as e:
        return {"error": str(e)}

@router.post("/ia/describe_image")
def describir_imagen(image_path: str):
    try:
        image = Image.open(image_path).convert('RGB')
        inputs = processor(image, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model_blip.generate(**inputs, max_new_tokens=100)
        caption = processor.decode(out[0], skip_special_tokens=True)
        return {"caption": caption}
    except Exception as e:
        return {"error": str(e)}
