# ==============================================================================================
#                                      APPLICATION ENTRY POINT
# - Starts the asyncio event loop and boots the WebSocket server.
# - Kept minimal on purpose: any future startup logic (DB connections, schedulers, etc.)
#   should be added here, not inside ws_service.py.
# ==============================================================================================
import asyncio
from infrastructure.database.database import Session
from testing.clear_database import clear_all_database
from testing.seed_database import seed_database
from ws_service import start_server

def reset_and_seed():
    with Session() as session:
        clear_all_database(session)
    seed_database()


if __name__ == "__main__":
    try:
        reset_and_seed()
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Python server stopped.", flush=True)