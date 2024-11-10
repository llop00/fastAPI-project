# app/core/config.py

import os
from dotenv import load_dotenv

# Cargar variables del entorno desde el archivo .env
load_dotenv()

FREEPIK_API_KEY = os.environ.get("FREEPIK_API_KEY")

# Carga de tokens y credenciales
INSTA_USER_ID = os.environ.get('INSTA_USER_ID')
INSTA_ACCESS_TOKEN = os.environ.get('INSTA_ACCESS_TOKEN')
IMGBB_API_KEY = os.environ.get('IMGBB_API_KEY')
IG_USER_ID = os.environ.get('IG_USER_ID')
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
HUGGING_FACE_TOKEN = os.environ.get('HUGGING_FACE_TOKEN')

# Configuración de correo electrónico
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))  # Puerto por defecto 587
SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')

# Variables de autenticación de Google
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
if GOOGLE_CLIENT_ID is None:
    raise Exception("GOOGLE_CLIENT_ID no está configurado en las variables de entorno")

# Clave secreta para JWT
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
if JWT_SECRET_KEY is None:
    raise Exception("JWT_SECRET_KEY no está configurado en las variables de entorno")
