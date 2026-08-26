import json
import asyncio
import websockets
from router import route_message
from infrastructure.database.database import Session
from modules.sports.strength_training.exercise import Exercise
from modules.sports.strength_training.workout import Workout, WorkoutExercise, SetLog
from infrastructure.database.repositories.sports.workout_repository import WorkoutRepository
from infrastructure.database.repositories.sports.exercise_repository import ExerciseRepository


connected_clients: set = set()

async def handler(websocket):
    connected_clients.add(websocket)
    print(f"Cliente conectado. Total: {len(connected_clients)}")
    
    # try:
    #     with Session() as session:
    #         repo = ExerciseRepository(session)
    #         exercises_dict = repo.get_all_as_dict()

    #     await websocket.send(json.dumps({
    #         "type": "exercises_loaded",
    #         "payload": exercises_dict
    #     }))
    # except Exception as e:
    #     print(f"Error al enviar ejercicios iniciales -> {e}", flush=True)

    try:
        async for message in websocket:
            await handle_message(websocket, message)
    
    except websockets.exceptions.ConnectionClosed:
        print("Cliente desconectado", flush=True)
    
    finally:
        connected_clients.remove(websocket)


async def handle_message(websocket, raw_message):
    try:
        data = json.loads(raw_message)
    except json.JSONDecodeError:
        print(f"Mensaje no válido (no es JSON): {raw_message}", flush=True)
        return

    msg_type: str = data.get("type")
    payload: dict = data.get("payload")
    print(f"Mensaje recibido -> type: {msg_type}, payload: {payload}", flush=True)
    
    was_handled = await route_message(websocket, msg_type, payload)
    if not was_handled: 
        print(f"No handler found for message type: {msg_type}", flush=True)
    
    response: dict = {"type": "ack", "received": data}
    await websocket.send(json.dumps(response))


async def start_server(host="localhost", port=8765):
    from infrastructure.database.database import init_db
    init_db()
    print(f"Servidor WebSocket escuchando en ws://{host}:{port}", flush=True)
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # se mantiene corriendo indefinidamente