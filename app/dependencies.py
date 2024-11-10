# app/dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload  # Puedes devolver el payload o información del usuario
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Token inválido")
