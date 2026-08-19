import asyncio
import json
import websockets
from modules.sports.strength_training.exercise import Exercise
from modules.sports.strength_training.workout import Workout, WorkoutExercise, SetLog
from infrastructure.database.database import Session, init_db
from infrastructure.database.repositories.sports.exercise_repository import ExerciseRepository
from infrastructure.database.repositories.sports.workout_repository import WorkoutRepository


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
        # ---  Exercise validation
        errors: list = Exercise.validate(payload)
        if  errors:
            await websocket.send(json.dumps({"type": "invalid_exercise", "payload": {"errors": errors}}))
            return
        
        exercise: object[Exercise] = Exercise(name = payload["name"], muscles = payload["muscles"], bodyweighted = payload["bodyweighted"])

        # --- Transaaction
        try: 
            # Database Insertion 
            with Session() as session:
                repo = ExerciseRepository(session)
                saved_exercise = repo.create(
                    name=exercise.name,
                    category=exercise.category,
                    bodyweighted=exercise.bodyweighted,
                    muscles_data=exercise.muscles
                )
            print(f"\n---- INSETRED INTO TABLE exercise VALUES (\n\tname={exercise.name})\n\tcategory={exercise.category}\n\tbodyweighted={exercise.bodyweighted}\n\tmuscles={exercise.muscles}\n)")
        
            # Message for frontend -> Transaction done
            await websocket.send(json.dumps({
                "type": "exercise_saved",
                "payload": {"name": exercise.name, "muscles": exercise.muscles, "bodyweighted": exercise.bodyweighted, "category": exercise.category}
            }))
            
            return
        
        except Exception as e:
            # ERROR MANAGING -> Message for frontend -> Transaction  failed
            print(f"Error al guardar ejercicio en BD -> {e}")
            await websocket.send(json.dumps({
                "type": "invalid_exercise",
                "payload": {"errors": ["Could not save the exercise to the database."]}
            }))

        return
        
    
    # ------------ NEW WORKOUT
    if msg_type == "save_workout":
        # --- Workout validation 
        errors: list = Workout.validate(payload)
        if errors:
            await websocket.send(json.dumps({
                "type": "invalid_workout",
                "payload": {"errors": errors}
            }))
            return
        
        exercises: list[WorkoutExercise] = []
        for exercise_data in payload["exercises"]:
            name: str = exercise_data["name"]
            # set_data - {'weight': 45, 'reps': 12, 'reached_failure': False},
            sets: list [SetLog] = [SetLog(**set_data) for set_data in exercise_data["sets"]]
            exercises.append(WorkoutExercise(name = name, sets = sets))
            
        workout: object[Workout] = Workout(
            date = payload["date"],
            satisfaction = payload["satisfaction"],
            intensity = payload["intensity"],
            exercises = exercises
        )
        
        # --- Transaction
        try: 
            with Session() as session:
                repo = WorkoutRepository(session)
                saved_exercise = repo.create(workout)

                # print(f"\nWorkout saved -> Date: {payload['date']} | Satisfaction: {payload['satisfaction']} | Intensity: {payload['intensity']} | Exercises: {len(exercises)}", flush=True)
                print(f"\n---- INSETRED INTO TABLE workout VALUES (\n\tdate: = {workout.date})\n\tsatiscatction={workout.satisfaction}\n\tintensity={workout.intensity}\n\texercises=overengineering print\n\tcreated_at: {workout._created_at}\n)")

            # Message for frontend -> Transaction done
            await websocket.send(json.dumps({
                "type": "workout_saved",
                "payload": {}
            }))    
            return
        
        except Exception as e:
            # Error managing -> Message for frontend -> Transaction  failed
            print(f"Error saving workout into database -> {e}", flush=True)
            await websocket.send(json.dumps({
                "type": "invalid_workout",
                "payload": {"errors": ["Could not save the workout to the database."]}
            }))
        
        return
        
        
    response: dict = {"type": "ack", "received": data}
    await websocket.send(json.dumps(response))


async def start_server(host="localhost", port=8765):
    init_db()
    print(f"Servidor WebSocket escuchando en ws://{host}:{port}", flush=True)
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # se mantiene corriendo indefinidamente