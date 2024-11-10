# app/main.py
import logging
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.api import freepik, instagram, imgbb, auth  # Añade auth
from app.api.freepik import generate_image_from_prompt
from app.api.imgbb import upload_image
from app.api.instagram import post_image_to_instagram
from app.api import calculator 
from pydantic import BaseModel
from app.utils.email_utils import send_email
from PIL import Image
import io

# Configuración del logger para la aplicación principal
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

# Crear manejador de consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Formato de logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Añadir manejador al logger
logger.addHandler(console_handler)

app = FastAPI()

logger.info("Iniciando la aplicación FastAPI")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.debug("Middleware CORS configurado")

# Incluir routers de las APIs
app.include_router(instagram.router)
app.include_router(freepik.router)
app.include_router(imgbb.router)
app.include_router(auth.router)
app.include_router(calculator.router)
logger.debug("Routers incluidos: instagram, freepik, imgbb, auth")

# Modelo Pydantic para la validación de datos
class GenerateAndPostModel(BaseModel):
    prompt: str
    caption: str = ''  # El caption es opcional, por defecto será una cadena vacía

@app.get("/")
def root():
    logger.info("Solicitud GET a '/' recibida")
    return {"message": "Backend de AutoPoster funcionando correctamente"}

# Ruta POST para generar y publicar la imagen
@app.post("/generate_and_post")
def generate_and_post(data: GenerateAndPostModel, background_tasks: BackgroundTasks):
    logger.info("Solicitud POST a '/generate_and_post' recibida")
    try:
        # Paso 1: Generar la imagen usando la API de Freepik
        logger.debug(f"Generando imagen con el prompt: {data.prompt}")
        freepik_result = generate_image_from_prompt(data.prompt)
        logger.debug(f"Resultado de Freepik: {freepik_result}")
        if "error" in freepik_result:
            logger.error(f"Error al generar imagen con Freepik: {freepik_result['error']}")
            return {"error": freepik_result["error"]}

        image_url = freepik_result["image_url"]
        logger.debug(f"URL de la imagen generada: {image_url}")

        # Paso 2: Subir la imagen a Instagram usando la URL pública generada por Freepik
        logger.debug(f"Publicando imagen en Instagram con URL: {image_url} y caption: {data.caption}")
        insta_result = post_image_to_instagram(image_url, data.caption)
        logger.debug(f"Resultado de Instagram: {insta_result}")
        if "error" in insta_result:
            logger.error(f"Error al publicar en Instagram: {insta_result['error']}")
            return {"error": insta_result["error"]}

        # Enviar correo electrónico en segundo plano
        subject = "Imagen generada y publicada en Instagram"
        body = f"Tu imagen generada con el prompt '{data.prompt}' ha sido publicada en Instagram con éxito."
        logger.debug("Añadiendo tarea de envío de correo electrónico en segundo plano")
        background_tasks.add_task(send_email, subject, body)

        logger.info("Imagen generada y publicada en Instagram con éxito")
        return {"message": "Imagen generada con Freepik y publicada en Instagram con éxito"}
    except Exception as e:
        logger.exception("Error inesperado en '/generate_and_post'")
        return {"error": "Error interno del servidor"}

# Nuevo endpoint para subir y publicar una imagen desde un archivo
@app.post("/upload_and_post_image")
def upload_and_post_image(
    background_tasks: BackgroundTasks,
    image_file: UploadFile = File(...),
    caption: str = Form('')
):
    logger.info("Solicitud POST a '/upload_and_post_image' recibida")
    try:
        # Paso 1: Leer el archivo y convertirlo a bytes
        logger.debug(f"Recibiendo archivo: {image_file.filename}")
        image_bytes = image_file.file.read()
        logger.debug(f"Bytes del archivo leídos: {len(image_bytes)} bytes")

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)
        image_bytes = buffer.read()
        logger.debug("Imagen convertida a JPEG exitosamente")

        # Paso 3: Subir la imagen a IMGBB
        logger.debug("Subiendo imagen a IMGBB")
        imgbb_result = upload_image(image_bytes)
        logger.debug(f"Resultado de IMGBB: {imgbb_result}")
        if "error" in imgbb_result:
            logger.error(f"Error al subir imagen a IMGBB: {imgbb_result['error']}")
            return {"error": imgbb_result["error"]}

        image_url = imgbb_result["data"]["url"]
        logger.debug(f"URL de la imagen subida a IMGBB: {image_url}")

        # Paso 4: Subir la imagen a Instagram usando la URL pública de IMGBB
        logger.debug(f"Publicando imagen en Instagram con URL: {image_url} y caption: {caption}")
        insta_result = post_image_to_instagram(image_url, caption)
        logger.debug(f"Resultado de Instagram: {insta_result}")
        if "error" in insta_result:
            logger.error(f"Error al publicar en Instagram: {insta_result['error']}")
            return {"error": insta_result["error"]}

        # Enviar correo electrónico en segundo plano
        subject = "Imagen subida y publicada en Instagram"
        body = "Tu imagen ha sido subida y publicada en Instagram con éxito."
        logger.debug("Añadiendo tarea de envío de correo electrónico en segundo plano")
        background_tasks.add_task(send_email, subject, body)

        logger.info("Imagen subida y publicada en Instagram con éxito")
        return {"message": "Imagen subida y publicada en Instagram con éxito"}
    except Exception as e:
        logger.exception("Error inesperado en '/upload_and_post_image'")
        return {"error": "Error interno del servidor"}

# Ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando el servidor Uvicorn")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
