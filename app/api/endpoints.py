from pydantic import BaseModel
from typing import Optional

# Esquema para la petición del usuario (Request)
class ChatRequest(BaseModel):
    session_id: str
    message: str

# Esquema para el resumen final
class UserSummary(BaseModel):
    name: str
    age: int
    goal: str

# Esquema para la respuesta de la API (Response)
class ChatResponse(BaseModel):
    response: str
    is_final: bool = False
    summary: Optional[UserSummary] = None
