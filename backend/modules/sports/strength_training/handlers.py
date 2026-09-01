import json
from .exercise import Exercise
from pprint import pprint
from infrastructure.database.database import Session
from .workout import Workout, WorkoutExercise, SetLog
from modules.sports.strength_training.data_loader import StrengthTrainingdataLoader
from infrastructure.database.repositories.sports.workout_repository import WorkoutRepository
from infrastructure.database.repositories.sports.exercise_repository import ExerciseRepository


async def handle_save_exercise(websocket, payload):
    # ---  Exercise validation
    errors: list = Exercise.validate(payload)
    if  errors:
        await websocket.send(json.dumps({"type": "invalid_exercise", "payload": {"errors": errors}}))
        return
            
    exercise: object[Exercise] = Exercise(name = payload["name"], muscles = payload["muscles"], bodyweighted = payload["bodyweighted"])
    
    # --- Transaaction
    try: 
        with Session() as session:
            repo = ExerciseRepository(session)
            saved_exercise = repo.create(
                name=exercise.name,
                category=exercise.category,
                bodyweighted=exercise.bodyweighted,
                muscles_data=exercise.muscles
            )
    except Exception as e:
        print(f"Error al guardar ejercicio en BD -> {e}")
        await websocket.send(json.dumps({
            "type": "invalid_exercise",
            "payload": {"errors": ["Could not save the exercise to the database."]}
        }))
        return
            
    print(f"\n---- INSETRED INTO TABLE exercise VALUES (\n\tname={exercise.name})\n\tcategory={exercise.category}\n\tbodyweighted={exercise.bodyweighted}\n\tmuscles={exercise.muscles}\n)")
            
    await websocket.send(json.dumps({
        "type": "exercise_saved",
        "payload": {"name": exercise.name, "muscles": exercise.muscles, "bodyweighted": exercise.bodyweighted, "category": exercise.category}
    }))
    
    
async def handle_save_workout(websocket, payload):
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
    except Exception as e:
        print(f"Error saving workout into database -> {e}", flush=True)
        await websocket.send(json.dumps({
            "type": "invalid_workout",
            "payload": {"errors": ["Could not save the workout to the database."]}
        }))
        return
    
            
    print(f"\n---- INSETRED INTO TABLE workout VALUES (\n\tdate: = {workout.date})\n\tsatiscatction={workout.satisfaction}\n\tintensity={workout.intensity}\n\texercises=overengineering print\n\tcreated_at: {workout._created_at}\n)")
    
    await websocket.send(json.dumps({
        "type": "workout_saved",
        "payload": {}
    }))    
    
    
async def handle_get_strength_training_data(websocket, payload):
    with Session() as session:
        exercise_repo = ExerciseRepository(session)
        # workout_repo = WorkoutRepository(session)

        exercises: dict[str, dict] = exercise_repo.get_all_as_dict()
        # recent_workouts = workout_repo.get_recent(limit=10)  # método a crear en el repo
    print(f"EXERCISES ------- \n {exercises}")
    await websocket.send(json.dumps({
        "type": "strength_training_data_loaded",
        "payload": {
            "exercises": exercises
            # "workouts": [_workout_to_dict(w) for w in recent_workouts],
        }
    }))

async def handle_get_heatmap_data(websocket, payload):
    selected_year: str = payload.get("year")
    with Session() as session:
        workout_repo = WorkoutRepository(session)
        workouts: list[dict] = workout_repo.get_heatmap_data(selected_year)
        
    print("heatmap data loaded")
    print(json.dumps(workouts, indent=4))
    await websocket.send(json.dumps({
        "type": "heatmap_data_loaded",
        "payload": workouts,
    }))
# [ { "date": "2025-03-15", "satisfaction": "great", "intensity": "high" },
#   { "date": "2025-03-17", "satisfaction": "neutral", "intensity": "moderate" }
# ]

async def handle_get_general_progress_data(websocket, payload) -> list[dict]:
    general_progress = {}
    with Session() as session:
        workout_repo = WorkoutRepository(session)
        for category in ("push", "pull", "legs", "core"):
            raw_data = workout_repo.get_data_by_category(category)
            general_progress[category] = StrengthTrainingdataLoader.load_progress(raw_data)
    clean_data = StrengthTrainingdataLoader.build_general_progress_results(general_progress)
    await websocket.send(json.dumps({
        "type": "general_progress_data_loaded",
        "payload": clean_data,
    }))
    