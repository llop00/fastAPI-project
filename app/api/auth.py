# app/api/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Crear un router para las rutas de autenticación
router = APIRouter()

# Definir el modelo de datos que esperamos recibir
class GoogleAuthRequest(BaseModel):
    token: str

@router.post("/auth/google")
async def google_auth(data: GoogleAuthRequest):
    token = data.token  # Aquí accedemos al token enviado por el cliente
    print(token)
    print("Google Auth")
    print(data)
    # Aquí puedes añadir el procesamiento del token de Google, como verificarlo.
    
    # Ejemplo de respuesta, puedes personalizarlo según tus necesidades
    if not token:
        raise HTTPException(status_code=400, detail="Token is missing")
    
    return {"access_token": token}
