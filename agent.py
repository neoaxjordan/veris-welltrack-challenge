# import asyncio
# from app.service.chat_service import process_chat_message

# async def main():
#     print("--- WellTrack Agent (CLI Mode) ---")
#     session_id = "cli-test-user"
    
#     while True:
#         user_input = input("Usuario: ")
#         if user_input.lower() in ["salir", "exit", "quit"]:
#             break
            
#         result = await process_chat_message(session_id, user_input)
#         print(f"Agente: {result['response']}")
        
#         if result['is_final']:
#             print(f"\n--- FLUJO FINALIZADO ---")
#             print(f"Resumen: {result['summary']}")
#             break

# if __name__ == "__main__":
#     asyncio.run(main())