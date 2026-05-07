from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_community.memory import ConversationBufferMemory
from langchain_classic.memory import ConversationBufferMemory


from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional
from app.core.config import settings

# Modelo para extraer la información de forma estructurada
class UserData(BaseModel):
    nombre: Optional[str] = Field(None, description="Nombre del usuario")
    edad: Optional[int] = Field(None, description="Edad del usuario")
    objetivo: Optional[str] = Field(None, description="Objetivo: perder peso, ganar músculo o mejorar resistencia")

def get_welltrack_agent(session_id: str, memory_store: dict):
    """
    Configura el agente con memoria persistente por session_id.
    """
    if session_id not in memory_store:
        # 1. Creamos el contenedor de mensajes (historia)
        history = ChatMessageHistory()
        # 2. Lo envolvemos en el gestor de memoria que el LLM entiende
        memory_store[session_id] = ConversationBufferMemory(
            chat_memory=history,
            return_messages=True, 
            memory_key="history"
        )
    
    # Obtenemos la memoria ya configurada para esta sesión
    memory = memory_store[session_id]
    
    llm = ChatGroq(
        api_key=settings.groq_api_key, 
        model_name=settings.model_name,
        temperature=0 # Temperatura 0 para mayor consistencia
    )

    # Instrucción clave para el System Prompt
    system_prompt = """
    Eres "VIKY-1.0", la asistente virtual experta de WellTrack. 
    Tu personalidad es profesional, motivadora y muy organizada.

    Tu objetivo es registrar a nuevos usuarios siguiendo estos pasos:
    1. Saludar y presentarte como VIKY-1.0.
    2. Obtener el Nombre del usuario.
    3. Obtener la Edad.
    4. Obtener su Objetivo de salud (perder peso, ganar masa o resistencia).

    Reglas críticas:
    - Si el usuario te pregunta quién eres o cómo te llamas, responde con orgullo que eres VIKY-1.0 de WellTrack.
    - Si el usuario te pregunta algo diferente, responde brevemente y vuelve a preguntar por el dato que falta.
    - SOLO cuando tengas los TRES datos, debes generar el resumen final y despedirte.
    - No des por finalizada la sesión si falta alguno de los tres.
    """

    prompt = ChatPromptTemplate.from_messages([
        system_prompt,
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    return prompt | llm