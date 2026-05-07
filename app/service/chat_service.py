import json
from langchain_core.messages import HumanMessage
from app.core.agent_logic import get_welltrack_agent
from langchain_groq import ChatGroq
from app.core.config import settings

from pydantic import BaseModel, Field
from typing import Optional
import re
from app.core.agent_logic import get_welltrack_agent


memory_store = {}

# Modelo para validar la extracción
class UserProfile(BaseModel):
    nombre: Optional[str] = Field(None, description="Nombre del usuario")
    edad: Optional[int] = Field(None, description="Edad del usuario")
    objetivo: Optional[str] = Field(None, description="Objetivo de salud")

async def extraer_datos_estructurados(conversation_history):
    """
    Analiza el historial de chat y extrae los datos en formato JSON.
    """
    llm = ChatGroq(
        api_key=settings.groq_api_key, 
        model_name="llama-3.3-70b-versatile", 
        temperature=0
    )
    
    # Prompt de extracción (separado de la charla principal)
    prompt = f"""
    Analiza el siguiente historial de chat y extrae la información del usuario.
    Si un dato no ha sido mencionado explícitamente, usa null.
    
    Formatos admitidos para objetivo: "perder peso", "ganar músculo", "mejorar resistencia".
    
    Historial:
    {conversation_history}
    
    Responde estrictamente en formato JSON con estas llaves: "nombre", "edad", "objetivo".
    """
    
    try:
        response = llm.invoke(prompt)
        # Limpiamos la respuesta por si el LLM añade texto extra
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
            
        data = json.loads(content)
        return UserProfile(**data)
    except Exception as e:
        print(f"Error en extracción: {e}")
        return UserProfile(nombre=None, edad=None, objetivo=None)

async def process_chat_message(session_id: str, message: str):
    agent_chain = get_welltrack_agent(session_id, memory_store)
        
    # Respuesta del agente
    response = agent_chain.invoke({"input": message, "history": memory_store[session_id].load_memory_variables({})["history"]})
    memory_store[session_id].save_context({"input": message}, {"output": response.content})
    
    history_messages = memory_store[session_id].load_memory_variables({})["history"]
    full_conversation = "\n".join([f"{'Usuario' if isinstance(m, HumanMessage) else 'Agente'}: {m.content}" for m in history_messages])
    
    # Llamamos a la lógica de extracción
    is_final, summary = await check_if_flow_completed(full_conversation)
    
    return {
        "response": response.content,
        "is_final": is_final,
        "summary": summary
    }

async def check_if_flow_completed(conversation_text: str):
    """
    Usa el LLM para extraer datos estructurados. 
    Si los 3 campos están presentes, finaliza.
    """
    llm = ChatGroq(api_key=settings.groq_api_key, model_name=settings.model_name, temperature=0)
    
    extraction_prompt = f"""
    Analiza la siguiente conversación y extrae información en formato JSON.
    Campos requeridos: "name" (string), "age" (int), "goal" (string).
    El "goal" debe ser uno de estos: perder peso, ganar músculo, mejorar resistencia.
    Si falta algún dato, ponlo como null.
    
    Conversación:
    {conversation_text}
    
    Responde ÚNICAMENTE el JSON.
    """
    
    res = llm.invoke(extraction_prompt)
    try:
        data = json.loads(res.content)
        # Si no hay nulos, hemos terminado
        if all(data.values()):
            return True, data
    except:
        pass
        
    return False, None


# Función helper para extraer valores (asegúrate de que esté definida o impórtala)
async def process_chat_message_new(session_id: str, message: str, memory_store: dict):
    # 1. Obtener agente y generar respuesta
    agent_chain = get_welltrack_agent(session_id, memory_store)
    
    # Inyectamos historial manualmente como ya descubriste que funciona
    history_state = memory_store[session_id].load_memory_variables({})["history"]
    response = agent_chain.invoke({"input": message, "history": history_state})
    
    # Guardar en memoria
    memory_store[session_id].save_context({"input": message}, {"output": response.content})
    
    # 2. Preparar el historial completo para la extracción
    history_messages = memory_store[session_id].load_memory_variables({})["history"]
    full_conversation = "\n".join([
        f"{'Usuario' if isinstance(m, HumanMessage) else 'Viky'}: {m.content}" 
        for m in history_messages
    ])
    
    # 3. Extraer datos usando el LLM (más inteligente que el Regex)
    data = await extraer_datos_con_llm(full_conversation)
    
    # Determinar si terminamos (si no hay valores null)
    # Importante: Usamos las llaves exactas que espera tu frontend/Pydantic
    nombre = data.get("name")
    edad = data.get("age")
    objetivo = data.get("goal")

    # Debug en consola para que veas qué pasa
    print("\n" + "="*40)
    print(f"DEBUG VIKY - SESIÓN: {session_id}")
    print(f"EXTRACCIÓN -> Nombre: {nombre} | Edad: {edad} | Objetivo: {objetivo}")
    
    is_final = all([nombre, edad, objetivo])
    print(f"ESTADO FINALIZADO: {is_final}")
    print("="*40 + "\n")
    
    return {
        "response": response.content,
        "is_final": is_final,
        "summary": data if is_final else None
    }

async def extraer_datos_con_llm(history_text: str):
    llm = ChatGroq(api_key=settings.groq_api_key, model_name=settings.model_name, temperature=0)
    
    # El prompt mejorado para evitar que Viky se auto-identifique
    prompt = f"""
    Eres un extractor de datos profesional. Analiza la conversación entre 'Usuario' y 'Viky'.
    Extrae la información personal del USUARIO.
    
    REGLAS CRÍTICAS:
    1. El nombre debe ser el del Usuario, NUNCA 'Viky' ni 'Viky-1.0'.
    2. Si el usuario solo dice su nombre (ej: "Kratos"), identifícalo como el nombre.
    3. Si un dato no está, usa null.
    4. El 'goal' debe ser: 'perder peso', 'ganar músculo' o 'mejorar resistencia'.
    
    Conversación:
    {history_text}
    
    Responde ÚNICAMENTE un JSON con este formato:
    {{"name": string o null, "age": int o null, "goal": string o null}}
    """
    
    try:
        res = llm.invoke(prompt)
        content = res.content.strip()
        # Limpieza de markdown por si el modelo lo incluye
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error extrayendo datos: {e}")
        return {"name": None, "age": None, "goal": None}
