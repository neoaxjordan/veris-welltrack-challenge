from fastapi import FastAPI, HTTPException
from app.api.endpoints import ChatRequest, ChatResponse
from app.service.chat_service import process_chat_message
from app.service.chat_service import process_chat_message_new
from app.utils.memory_store import sessions_memory

# Instancia central de la aplicación
app = FastAPI(
    title="WellTrack Onboarding API",
    description="Agente conversacional para registro de usuarios"
)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 1. Validación de entrada (Bonus: Manejo de errores)
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")
            
        # 2. Llamada al orquestador que maneja la lógica y la memoria
        # result = await process_chat_message(request.session_id, request.message)
        result = await process_chat_message_new(
            session_id=request.session_id, 
            message=request.message, 
            memory_store=sessions_memory
        )
        
        # 3. Respuesta estructurada 
        return ChatResponse(
            response=result["response"],
            is_final=result["is_final"],
            summary=result["summary"]
        )
    except Exception as e:
        # Bonus: Manejo de errores inesperados
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/")
async def root():
    return {"message": "WellTrack API is running. Use /chat endpoint."}