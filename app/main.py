import logging
import io
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

from app.api import freepik, instagram, imgbb, auth, calculator, email
from app.api.freepik import generate_image_from_prompt
from app.api.imgbb import upload_image_to_imgbb
from app.api.scraper import router as scraper_router
from app.api.instagram import post_image_to_instagram
from app.utils.email_utils import send_email

# Configurar el logger principal
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Crear la aplicación FastAPI
app = FastAPI()
logger.info("Iniciando la aplicación FastAPI")

# Configuración del middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.debug("Middleware CORS configurado")

# Registrar routers
app.include_router(instagram.router)
app.include_router(freepik.router)
app.include_router(imgbb.router)
app.include_router(auth.router)
app.include_router(calculator.router)
app.include_router(email.router)
app.include_router(scraper_router)

logger.debug("Routers registrados: instagram, freepik, imgbb, auth, calculator, email")

# Modelo Pydantic
class GenerateAndPostModel(BaseModel):
    prompt: str
    caption: str = ""  # El caption es opcional

@app.get("/")
def root():
    logger.info("Solicitud GET a '/' recibida")
    return {"message": "Backend de AutoPoster funcionando correctamente"}

@app.post("/generate_and_post")
def generate_and_post(data: GenerateAndPostModel, background_tasks: BackgroundTasks):
    logger.info("Solicitud POST a '/generate_and_post' recibida")
    try:
        logger.debug(f"Generando imagen con el prompt: {data.prompt}")
        freepik_result = generate_image_from_prompt(data.prompt)
        if "error" in freepik_result:
            logger.error(f"Error al generar imagen: {freepik_result['error']}")
            return {"error": freepik_result["error"]}

        image_url = freepik_result["image_url"]
        logger.debug(f"Imagen generada: {image_url}")

        logger.debug(f"Publicando imagen en Instagram con URL: {image_url} y caption: {data.caption}")
        insta_result = post_image_to_instagram(image_url, data.caption)
        if "error" in insta_result:
            logger.error(f"Error al publicar en Instagram: {insta_result['error']}")
            return {"error": insta_result["error"]}

        subject = "Imagen generada y publicada en Instagram"
        body = f"Tu imagen generada con el prompt '{data.prompt}' ha sido publicada en Instagram con éxito."
        background_tasks.add_task(send_email, subject, body)

        logger.info("Imagen generada y publicada con éxito")
        return {"message": "Imagen generada y publicada con éxito"}
    except Exception as e:
        logger.exception("Error en '/generate_and_post'")
        return {"error": "Error interno del servidor"}

@app.post("/upload_and_post_image")
def upload_and_post_image(
    background_tasks: BackgroundTasks,
    image_file: UploadFile = File(...),
    caption: str = Form("")
):
    logger.info("Solicitud POST a '/upload_and_post_image' recibida")
    try:
        logger.debug(f"Procesando archivo: {image_file.filename}")
        image_bytes = image_file.file.read()

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)
        image_bytes = buffer.read()

        logger.debug("Subiendo imagen a IMGBB")
        imgbb_result = upload_image_to_imgbb(image_bytes)
        if "error" in imgbb_result:
            logger.error(f"Error al subir imagen a IMGBB: {imgbb_result['error']}")
            return {"error": imgbb_result["error"]}

        image_url = imgbb_result["data"]["url"]
        logger.debug(f"Imagen subida: {image_url}")

        logger.debug(f"Publicando imagen en Instagram con URL: {image_url} y caption: {caption}")
        insta_result = post_image_to_instagram(image_url, caption)
        if "error" in insta_result:
            logger.error(f"Error al publicar en Instagram: {insta_result['error']}")
            return {"error": insta_result["error"]}

        subject = "Imagen subida y publicada en Instagram"
        body = "Tu imagen ha sido subida y publicada en Instagram con éxito."
        background_tasks.add_task(send_email, subject, body)

        logger.info("Imagen subida y publicada con éxito")
        return {"message": "Imagen subida y publicada con éxito"}
    except Exception as e:
        logger.exception("Error en '/upload_and_post_image'")
        return {"error": "Error interno del servidor"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando el servidor Uvicorn")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
