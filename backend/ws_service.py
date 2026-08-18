import asyncio
import json
import websockets
from modules.sport.strength_training.exercise import Exercise
from modules.sport.strength_training.workout import Workout, WorkoutExercise, SetLog


connected_clients: set = set()

async def handler(websocket):
    connected_clients.add(websocket)
    print(f"Cliente conectado. Total: {len(connected_clients)}")

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
    
    # ------------ NEW EXERCISE
    if msg_type == "save_exercise":
        errors: list = Exercise.validate(payload)
        if  errors:
            await websocket.send(json.dumps({
                "type": "invalid_exercise",
                "payload": {"errors": errors}
            }))
            return
        
        exercise: object[Exercise] = Exercise(name = payload["name"], muscles = payload["muscles"], bodyweighted = payload["bodyweighted"])
        
        await websocket.send(json.dumps({
            "type": "exercise_saved",
            "payload": {"name": exercise.name, "muscles": exercise.muscles, "bodyweighted": exercise.bodyweighted, "category": exercise.category}
        }))
        return
    
    # ------------ NEW WORKOUT
    if msg_type == "save_workout":
        errors: list = Workout.validate(payload)
        if errors:
            await websocket.send(json.dumps({
                "type": "invalid_workout",
                "payload": {"errors": errors}
            }))
            return
        
        exercises: list[WorkoutExercise] = []
        for exercise_data in payload["exercises"]:
            sets: list [SetLog] = [SetLog(**set) for set in exercise_data["sets"]]
            exercises.append(WorkoutExercise(name = exercise_data["name"], sets = sets))
            
        workout: object[Workout] = Workout(
            date = payload["date"],
            satisfaction = payload["satisfaction"],
            intensity = payload["intensity"],
            exercises = exercises
        )

        print(f"\nWorkout saved -> Date: {payload['date']} | Satisfaction: {payload['satisfaction']} | Intensity: {payload['intensity']} | Exercises: {len(exercises)}", flush=True)
        
        await websocket.send(json.dumps({
            "type": "workout_saved",
            "payload": {}
        }))
        return
        
        
    response: dict = {"type": "ack", "received": data}
    await websocket.send(json.dumps(response))


async def start_server(host="localhost", port=8765):
    print(f"Servidor WebSocket escuchando en ws://{host}:{port}", flush=True)
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # se mantiene corriendo indefinidamente