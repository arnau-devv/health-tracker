# ==============================================================================================
#                                      APPLICATION ENTRY POINT
# - Starts the asyncio event loop and boots the WebSocket server.
# - Kept minimal on purpose: any future startup logic (DB connections, schedulers, etc.)
#   should be added here, not inside ws_service.py.
# ==============================================================================================
import asyncio
from ws_service import start_server

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Python server stopped.", flush=True)