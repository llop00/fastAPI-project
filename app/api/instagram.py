# app/api/instagram.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.config import INSTA_USER_ID, INSTA_ACCESS_TOKEN, IMGBB_API_KEY
import requests
from app.dependencies import verify_token

router = APIRouter()

# Definimos ImageUploadModel para validar los datos recibidos
class ImageUploadModel(BaseModel):
    image_base64: str
    caption: str = ''

@router.get("/instagram/login")
def instagram_login(user=Depends(verify_token)):
    url = f"https://graph.instagram.com/{INSTA_USER_ID}?fields=id,username&access_token={INSTA_ACCESS_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {"username": data['username'], "id": data['id']}
    else:
        return {"error": response.json().get('error', {}).get('message', 'Error desconocido')}

@router.get("/instagram/media")
def get_user_media(user=Depends(verify_token)):
    url = f"https://graph.instagram.com/{INSTA_USER_ID}/media?fields=id,caption,media_url,media_type&access_token={INSTA_ACCESS_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        return {"error": response.json().get('error', {}).get('message', 'Error desconocido')}

@router.post("/instagram/upload_image")
def post_image_to_instagram(image_url: str, caption: str = '', user=Depends(verify_token)):
    upload_url = f"https://graph.instagram.com/{INSTA_USER_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': INSTA_ACCESS_TOKEN
    }
    response = requests.post(upload_url, data=payload)
    if response.status_code == 200:
        media_id = response.json().get('id')
        publish_url = f"https://graph.instagram.com/{INSTA_USER_ID}/media_publish"
        publish_payload = {
            'creation_id': media_id,
            'access_token': INSTA_ACCESS_TOKEN
        }
        publish_response = requests.post(publish_url, data=publish_payload)
        if publish_response.status_code == 200:
            return {"message": "Imagen publicada con éxito"}
        else:
            return {"error": "Error al publicar la imagen"}
    else:
        return {"error": "Error al subir la imagen"}

@router.post("/instagram/upload_image_base64")
def post_image_to_instagram_base64(data: ImageUploadModel, user=Depends(verify_token)):
    image_base64 = data.image_base64
    caption = data.caption
    # Subir la imagen a IMGBB para obtener una URL pública
    imgbb_url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": image_base64,
    }

    imgbb_response = requests.post(imgbb_url, data=payload)

    if imgbb_response.status_code == 200:
        imgbb_data = imgbb_response.json().get("data", {})
        image_url = imgbb_data.get("url")

        # Publicar la imagen en Instagram
        insta_url = f"https://graph.instagram.com/{INSTA_USER_ID}/media"
        insta_payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": INSTA_ACCESS_TOKEN,
        }

        insta_response = requests.post(insta_url, data=insta_payload)
        if insta_response.status_code == 200:
            media_id = insta_response.json().get("id")
            publish_url = f"https://graph.instagram.com/{INSTA_USER_ID}/media_publish"
            publish_payload = {
                "creation_id": media_id,
                "access_token": INSTA_ACCESS_TOKEN,
            }

            publish_response = requests.post(publish_url, data=publish_payload)
            if publish_response.status_code == 200:
                return {"message": "Imagen publicada con éxito en Instagram"}
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Error al publicar la imagen en Instagram"
                )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al crear media en Instagram"
            )
    else:
        raise HTTPException(
            status_code=500,
            detail="Error al subir la imagen a IMGBB"
        )
