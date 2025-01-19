import os
import openai
import smtplib
import logging
import requests
import re

from fastapi import APIRouter, Body, HTTPException
from email.message import EmailMessage

# Importamos la función que genera la imagen en Freepik (base64)
from app.api.freepik import generate_image_from_prompt, PromptRequest
# Importamos la función para subir la imagen a Imgbb y obtener URL + delete_url
from app.api.imgbb import upload_image_to_imgbb

router = APIRouter()

def remove_code_fences(text: str) -> str:
    """
    Elimina posibles bloques de código (triple backticks) de la respuesta
    para asegurarnos de que no incluya snippets de código.
    """
    return text.replace("```html", "").replace("```", "")

def strip_html_tags(html: str) -> str:
    """
    Elimina etiquetas HTML para quedarnos solo con el texto plano.
    """
    # Quitamos las etiquetas <...>
    text = re.sub(r"<[^>]+>", "", html)
    # Convertimos secuencias de espacios en uno solo
    text = re.sub(r"\s+", " ", text).strip()
    return text

@router.post("/send-structured-email")
async def send_structured_email(
    recipients: list[str] = Body(..., example=["destino@example.com"]),
    subject: str = Body(..., example="Asunto del correo"),
    topic: str = Body(..., example="Tema del correo")
):
    """
    Endpoint para generar y enviar un correo estructurado sobre 'topic'.
    Emplea OpenAI para:
      1) Crear una 'estructura' de secciones.
      2) Generar contenido HTML con placeholders xXIMAGENXx.
    Luego, cada xXIMAGENXx se sustituye por una imagen generada en Freepik
    y subida a Imgbb, para obtener la URL y NO incrustar base64 en el correo.
    Finalmente, al terminar, se borra la imagen de Imgbb.
    
    Se ha mejorado la apariencia con un estilo más limpio, títulos más grandes,
    separaciones generosas y colores neutros.
    """
    try:
        logging.info("Generando estructura del correo...")

        # Configuramos la API Key de OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise HTTPException(
                status_code=500,
                detail="No se ha configurado la clave de API de OpenAI."
            )

        # 1) Pedimos a ChatGPT la estructura en texto plano
        structure_prompt = (
            f"Genera una estructura muy detallada para un correo sobre '{topic}'. "
            "Devuélvela en una lista en texto plano (ejemplo: [Sección1, Sección2, Subsección2.1, ...]). "
            "Sin explicaciones ni markdown, ni snippets de codigo."
        )
        structure_response = await openai.ChatCompletion.acreate(
            model=os.getenv("GPT_MODEL"),
            messages=[
                {"role": "system", "content": "Eres un asistente que crea estructuras de correo."},
                {"role": "user", "content": structure_prompt}
            ],
            max_tokens=400,
            temperature=1.0
        )
        structure = structure_response.choices[0].message.content.strip()
        if not structure:
            raise HTTPException(500, "No se generó la estructura del correo.")
        structure = remove_code_fences(structure)

        logging.info("Generando contenido en HTML con placeholders de imágenes...")

        # 2) Generar contenido HTML, usando xXIMAGENXx como placeholder
        content_prompt = (
            f"Utiliza esta estructura para generar el contenido de un correo HTML: {structure}. "
            f"El tema es: {topic}. Emplea encabezados (<h2>, <h3>), párrafos (<p>), listas (<ul>, <li>) "
            "y coloca la cadena 'xXIMAGENXx' cada vez que necesites una imagen, al menos cada dos secciones. "
            "No incluyas la etiqueta <img>. No añadas alt, style ni nada; solo xXIMAGENXx. "
            "No uses snippets de código. No incluyas títulos como 'Sección:' o 'Conclusión:'. "
            "Asegúrate de que el texto sea amplio y descriptivo."
            "No quiero que en ningun momento se referencie al usuario por su nombre. Si se refiere a él, que sea de manera general o como 'estimado lector' o cosas parecidas."
        )
        content_response = await openai.ChatCompletion.acreate(
            model=os.getenv("GPT_MODEL"),
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente que redacta correos HTML con placeholders para imágenes."
                },
                {"role": "user", "content": content_prompt}
            ],
            max_tokens=3000,
            temperature=0.9
        )
        html_body = content_response.choices[0].message.content.strip()
        if not html_body:
            raise HTTPException(500, "No se generó el contenido en HTML.")
        html_body = remove_code_fences(html_body)

        logging.info("Reemplazando xXIMAGENXx por <img src='URL'>...")

        pattern = "xXIMAGENXx"
        delete_urls = []

        # Expresión regular para localizar <h2> o <h3> con su contenido
        heading_pattern = re.compile(r"<(h[23])>(.*?)</\1>", re.DOTALL | re.IGNORECASE)

        # Mientras haya placeholders
        while pattern in html_body:
            pos_placeholder = html_body.index(pattern)

            # Buscamos la sección que abarca este placeholder
            all_headings = list(heading_pattern.finditer(html_body))
            last_heading_index = -1
            for match in all_headings:
                start, end = match.span()
                if end < pos_placeholder:
                    last_heading_index = start
                else:
                    break

            # Hallamos el HTML de la sección
            if last_heading_index == -1:
                section_html = html_body[:pos_placeholder].strip() or topic
            else:
                current_heading_match = heading_pattern.search(html_body, last_heading_index)
                if current_heading_match:
                    start_heading = current_heading_match.start()
                    # Buscamos la siguiente heading
                    subsequent_match = heading_pattern.search(html_body, current_heading_match.end())
                    if subsequent_match and subsequent_match.start() < pos_placeholder:
                        section_html = html_body[start_heading:subsequent_match.start()]
                    else:
                        section_html = html_body[start_heading:pos_placeholder]
                else:
                    section_html = html_body[:pos_placeholder]

            # Texto plano de la sección
            text_section = strip_html_tags(section_html)

            # Prompt detallado para la imagen
            detailed_prompt = (
                f"Genera una imagen muy descriptiva y detallada sobre el siguiente contenido: '{text_section}'. "
                f"El tema global es '{topic}'. "
                "Usa un estilo fotográfico con elementos relevantes que reflejen dicho contenido."
            )

            # Obtenemos la imagen (base64)
            try:
                freepik_resp = generate_image_from_prompt(PromptRequest(prompt=detailed_prompt))
                base64_image = freepik_resp.get("image_base64", "")
            except Exception as e:
                logging.error(f"Error al generar imagen con Freepik: {str(e)}")
                base64_image = ""

            replacement = ""
            if base64_image:
                # Subimos a Imgbb
                try:
                    imgbb_data = upload_image_to_imgbb(base64_image, expiration=60)
                    image_url = imgbb_data["url"]
                    delete_url = imgbb_data["delete_url"]
                    delete_urls.append(delete_url)
                except Exception as e:
                    logging.error(f"Error al subir imagen a Imgbb: {str(e)}")
                    image_url = ""

                if image_url:
                    replacement = (
                        f'<img src="{image_url}" '
                        'alt="Imagen generada" style="max-width:100%;height:auto;" />'
                    )

            # Reemplazamos la primera ocurrencia del placeholder
            html_body = (
                html_body[:pos_placeholder]
                + replacement
                + html_body[pos_placeholder + len(pattern):]
            )

        logging.info("Construyendo correo final...")

        # Plantilla HTML final con estilos más neutrales y separaciones
        full_html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8" />
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    background-color: #f2f2f2;
                }}
                .container {{
                    max-width: 700px;
                    margin: 40px auto;
                    background-color: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                    padding: 30px;
                }}
                .header {{
                    background-color: #555;
                    text-align: center;
                    padding: 40px 20px;
                    border-radius: 8px 8px 0 0;
                }}
                .header h1 {{
                    color: #fff;
                    margin: 0;
                    font-size: 34px;
                }}
                /* Estilos para contenido interno */
                .content h2 {{
                    margin-top: 30px;
                    margin-bottom: 15px;
                    font-size: 24px;
                    color: #333;
                }}
                .content h3 {{
                    margin-top: 25px;
                    margin-bottom: 12px;
                    font-size: 20px;
                    color: #444;
                }}
                .content p {{
                    margin-bottom: 18px;
                    line-height: 1.6;
                    font-size: 15px;
                    color: #555;
                }}
                .content ul {{
                    margin-left: 20px;
                    margin-bottom: 18px;
                    color: #555;
                }}
                .content li {{
                    margin-bottom: 8px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 13px;
                    color: #666;
                    border-top: 1px solid #ddd;
                    margin-top: 40px;
                }}
                .footer a {{
                    color: #007BFF;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{subject}</h1>
                </div>
                <div class="content">
                    {html_body}
                </div>
                <div class="footer">
                    <p>¿Tienes preguntas? <a href="mailto:soporte@ejemplo.com">Contáctanos</a></p>
                    <p>Síguenos en 
                        <a href="https://www.twitter.com">Twitter</a> | 
                        <a href="https://www.facebook.com">Facebook</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        # Construimos el mensaje de correo
        msg = EmailMessage()
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        # Parte de texto alternativo
        msg.set_content(
            "Este correo está diseñado en HTML, por favor utiliza un cliente que lo soporte.\n\n"
            f"Estructura:\n{structure}\n\n"
            f"Contenido (HTML):\n{html_body}\n\n"
            "Las imágenes se han subido a Imgbb tras generarse con Freepik."
        )

        # Parte HTML
        msg.add_alternative(full_html, subtype="html")

        # Credenciales de email
        email_user = os.getenv("EMAIL_USER")
        email_pass = os.getenv("EMAIL_PASS")
        if not email_user or not email_pass:
            raise HTTPException(500, "Credenciales de correo no configuradas.")

        # Enviar correo
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)

        logging.info("Correo enviado exitosamente.")

        # Borramos las imágenes de Imgbb con las delete_urls
        for durl in delete_urls:
            try:
                requests.get(durl, timeout=10)
            except Exception as ex:
                logging.error(f"No se pudo borrar la imagen de Imgbb: {str(ex)}")

        return {"detail": "Correo enviado"}

    except openai.error.OpenAIError as e:
        logging.error(f"Error al interactuar con OpenAI: {e}")
        raise HTTPException(500, "Error al generar contenido con OpenAI.")
    except smtplib.SMTPException as e:
        logging.error(f"Error al enviar el correo: {e}")
        raise HTTPException(500, "Error al enviar el correo.")
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        raise HTTPException(500, "Ha ocurrido un error inesperado.")
