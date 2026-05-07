# WellTrack AI Onboarding Agent

Este proyecto es un agente conversacional de onboarding desarrollado para la plataforma WellTrack. Utiliza IA para recopilar información de registro (Nombre, Edad, Objetivo) de forma natural.

## Lógica de Memoria
* Persistencia: La memoria se gestiona por session_id. Si usas el mismo ID, el agente recordará lo dicho anteriormente.

* Extracción Estructurada: El agente utiliza un PydanticOutputParser para transformar la charla en un objeto JSON con los campos nombre, edad y objetivo.

## 🛠️ Stack Tecnológico
* **Python 3.10+**
* **LangChain**: Orquestador del agente y la memoria.
* **FastAPI**: Framework para la API.
* **Groq**: Motor de inferencia para el modelo Llama 3.3.

## 🚀 Instalación y Uso

1. **Clonar el repositorio** e ingresar a la carpeta.
2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

## Instalar dependencias
   ```bash
   pip install -r requirements.txt
   ```

## Configuracion de variables
* Crear un archivo **.env** basado en **.env.example** y agrega tu **GROQ_API_KEY**.

## 🖥️ Ejecución
* Para iniciar la API, ejecuta desde la raíz:
   ```bash
   python main.py
   ```
* La API estará disponible en http://localhost:8000.

## 🧪 Pruebas (curl)
   ```bash
    curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "user123", "message": "Hola"}'
   ```

---

**Autor**: Alex Daniel Jordan Veliz
- *Líder Técnico & Arquitecto de Soluciones & FullStack Senior*