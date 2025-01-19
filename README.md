# FastAPI Project

## Descripción

Este proyecto es un backend desarrollado con **FastAPI** para gestionar múltiples servicios, como la generación de imágenes mediante Freepik, publicación en Instagram, subida de imágenes a ImgBB y envío de correos electrónicos. Está diseñado para ser modular y fácilmente extensible.

---

## Tabla de Contenidos

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Servicios Principales](#servicios-principales)
- [API Endpoints](#api-endpoints)

---

## Requisitos

- **Python 3.9 o superior**
- **Docker y Docker Compose** (para ejecutar con contenedores)
- **Cuenta y claves API** para los servicios:
  - Freepik
  - ImgBB
  - OpenAI
  - Instagram
  - Correo SMTP

---

## Instalación

1. Clona este repositorio:

   ```bash
   git clone <tu-repositorio>
   cd <nombre-del-directorio>
   ```

2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Configura las variables de entorno creando un archivo `.env` en la raíz del proyecto. Consulta la sección [Configuración](#configuración).

---

## Configuración

Ejemplo del archivo `.env`:

```env
FREEPIK_API_KEY=tu_clave_de_freepik
IMGBB_API_KEY=tu_clave_de_imgbb
OPENAI_API_KEY=tu_clave_de_openai
EMAIL_USER=tu_correo
EMAIL_PASS=tu_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
INSTA_USER_ID=tu_instagram_user_id
INSTA_ACCESS_TOKEN=tu_instagram_access_token
GPT_MODEL=gpt-4
```

**Nota:** Asegúrate de usar valores reales para las claves API y credenciales.

---

## Ejecución

### Usando Docker Compose

1. Construye y ejecuta el contenedor:

   ```bash
   docker-compose up --build
   ```

2. La aplicación estará disponible en `http://localhost:8000`.

### Ejecución Local

1. Inicia el servidor con Uvicorn:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Accede a la documentación interactiva de la API:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Estructura del Proyecto

```
├── app/
│   ├── api/
│   │   ├── freepik.py          # Gestión de imágenes con Freepik
│   │   ├── imgbb.py            # Subida de imágenes a ImgBB
│   │   ├── email.py            # Envío de correos electrónicos
│   │   ├── instagram.py        # Publicación en Instagram
│   │   ├── auth.py             # Servicios de autenticación
│   │   ├── calculator.py       # API de calculadora
│   ├── utils/
│   │   └── email_utils.py      # Funciones de utilidades para correos
│   ├── main.py                 # Archivo principal del backend
├── Dockerfile                  # Archivo para construir la imagen Docker
├── docker-compose.yml          # Configuración de Docker Compose
├── requirements.txt            # Dependencias del proyecto
├── .env                        # Variables de entorno (no compartas este archivo públicamente)
```

---

## Servicios Principales

1. **Generación de imágenes (Freepik):** Genera imágenes basadas en texto utilizando la API de Freepik.
2. **Subida de imágenes (ImgBB):** Almacena imágenes y obtiene URLs públicas.
3. **Publicación en Instagram:** Publica imágenes en cuentas de Instagram mediante su API oficial.
4. **Envío de correos electrónicos:** Envía correos electrónicos automatizados con SMTP.

---

## API Endpoints

### Endpoints de Imagen
- `POST /freepik/generate_image`: Genera imágenes con Freepik.
- `POST /imgbb/upload`: Sube imágenes a ImgBB.
- `POST /instagram/upload_image`: Publica imágenes en Instagram.

### Endpoints de Correo
- `POST /send-structured-email`: Genera y envía correos electrónicos dinámicos.

### Otros Endpoints
- `POST /generate_and_post`: Genera una imagen y la publica en Instagram.
- `POST /upload_and_post_image`: Sube una imagen y la publica en Instagram.

---

Con este README, cualquier persona debería poder configurar y ejecutar tu aplicación sin problemas. Si necesitas agregar más información o ejemplos, avísame. 😊
