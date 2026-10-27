"""
Script para llenar la base de datos con entrenamientos realistas.
Crea ejercicios y workouts con progresión en peso/reps a lo largo de 2025-2026.
"""

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from infrastructure.database.database import Session as DBSession
from infrastructure.database.models.strength_training import (
    ExerciseModel,
    ExerciseMuscleModel,
    WorkoutModel,
    WorkoutExerciseModel,
    WorkoutExerciseMuscleModel,
    SetModel,
)


# ═════════════════════════════════════════════════════════════════════
# EJERCICIOS BASE
# ═════════════════════════════════════════════════════════════════════

EXERCISES_DATA = {
    # PUSH
    "bench press": {
        "category": "push",
        "bodyweighted": False,
        "muscles": {"chest": 0.7, "anterior_shoulder": 0.15, "triceps": 0.15},
    },
    "overhead press": {
        "category": "push",
        "bodyweighted": False,
        "muscles": {"anterior_shoulder": 0.6, "chest": 0.2, "triceps": 0.2},
    },
    "dips": {
        "category": "push",
        "bodyweighted": True,
        "muscles": {"triceps": 0.6, "chest": 0.3, "anterior_shoulder": 0.1},
    },
    "pushups": {
        "category": "push",
        "bodyweighted": True,
        "muscles": {"chest": 0.6, "triceps": 0.3, "anterior_shoulder": 0.1},
    },
    # PULL
    "deadlift": {
        "category": "pull",
        "bodyweighted": False,
        "muscles": {"lats": 0.4, "upper_back": 0.3, "biceps": 0.3},
    },
    "pull ups": {
        "category": "pull",
        "bodyweighted": True,
        "muscles": {"lats": 0.7, "biceps": 0.2, "upper_back": 0.1},
    },
    "bent over row": {
        "category": "pull",
        "bodyweighted": False,
        "muscles": {"upper_back": 0.6, "lats": 0.3, "biceps": 0.1},
    },
    # LEGS
    "squat": {
        "category": "legs",
        "bodyweighted": False,
        "muscles": {"quadriceps": 0.7, "glutes": 0.2, "hamstrings": 0.1},
    },
    "leg press": {
        "category": "legs",
        "bodyweighted": False,
        "muscles": {"quadriceps": 0.8, "glutes": 0.15, "hamstrings": 0.05},
    },
    "lunges": {
        "category": "legs",
        "bodyweighted": False,
        "muscles": {"quadriceps": 0.6, "glutes": 0.3, "hamstrings": 0.1},
    },
    # CORE
    "planks": {
        "category": "core",
        "bodyweighted": True,
        "muscles": {"rectus_abdominis": 0.6, "obliques": 0.3, "lower_back": 0.1},
    },
    "ab wheel": {
        "category": "core",
        "bodyweighted": False,
        "muscles": {"rectus_abdominis": 0.8, "obliques": 0.15, "lower_back": 0.05},
    },
}

SATISFACTION_LEVELS = ["terrible", "bad", "neutral", "good", "great"]
INTENSITY_LEVELS = ["very_low", "low", "moderate", "high", "very_high"]

# ═════════════════════════════════════════════════════════════════════
# PROGRESIÓN DE PESO POR EJERCICIO
# ═════════════════════════════════════════════════════════════════════

EXERCISE_PROGRESSION = {
    "bench press": {"start": 40.0, "increment": 2.5, "interval_days": 14, "reps": [10, 12, 12]},
    "overhead press": {"start": 25.0, "increment": 2.0, "interval_days": 14, "reps": [8, 10, 10]},
    "dips": {"start": 0.1, "increment": 0, "interval_days": 7, "reps": [8, 8, 8]},  # bodyweight
    "pushups": {"start": 0.1, "increment": 0, "interval_days": 7, "reps": [15, 15, 15]},
    "deadlift": {"start": 80.0, "increment": 5.0, "interval_days": 21, "reps": [5, 5, 5]},
    "pull ups": {"start": 0.1, "increment": 0, "interval_days": 7, "reps": [5, 5, 5]},
    "bent over row": {"start": 60.0, "increment": 2.5, "interval_days": 14, "reps": [8, 10, 10]},
    "squat": {"start": 60.0, "increment": 5.0, "interval_days": 14, "reps": [8, 10, 10]},
    "leg press": {"start": 100.0, "increment": 10.0, "interval_days": 14, "reps": [10, 12, 12]},
    "lunges": {"start": 20.0, "increment": 2.5, "interval_days": 14, "reps": [10, 10, 10]},
    "planks": {"start": 0.1, "increment": 0, "interval_days": 7, "reps": [45, 45, 45]},  # segundos
    "ab wheel": {"start": 0.1, "increment": 0, "interval_days": 7, "reps": [12, 12, 12]},
}


def create_exercises(session: Session) -> dict[str, ExerciseModel]:
    """Crea todos los ejercicios en la BD."""
    exercises = {}

    for name, data in EXERCISES_DATA.items():
        muscles = [
            ExerciseMuscleModel(name=muscle, involvement=involvement)
            for muscle, involvement in data["muscles"].items()
        ]

        exercise = ExerciseModel(
            name=name,
            category=data["category"],
            bodyweighted=data["bodyweighted"],
            muscles=muscles,
        )
        session.add(exercise)
        exercises[name] = exercise

    session.commit()
    print(f"Creados {len(exercises)} ejercicios")
    return exercises


def get_weight_for_date(exercise_name: str, current_date: datetime) -> float:
    """Calcula el peso basado en la progresión esperada hasta esa fecha."""
    prog = EXERCISE_PROGRESSION[exercise_name]
    start_date = datetime(2025, 1, 1)
    days_elapsed = (current_date - start_date).days
    intervals_passed = days_elapsed // prog["interval_days"]

    current_weight = prog["start"] + (intervals_passed * prog["increment"])
    # Añadir variación aleatoria pequeña (±5%)
    variation = random.uniform(0.95, 1.05)
    return round(current_weight * variation, 1)


def create_workout_for_date(
    session: Session, workout_date: datetime, exercises_map: dict
) -> WorkoutModel:
    """Crea un workout para una fecha específica."""
    # Seleccionar 2-3 ejercicios aleatorios
    selected_exercises = random.sample(list(exercises_map.items()), random.randint(2, 3))

    workout_exercises = []
    for position, (exercise_name, exercise_model) in enumerate(selected_exercises):
        # Obtener progresión de peso para esa fecha
        prog = EXERCISE_PROGRESSION[exercise_name]
        weight = get_weight_for_date(exercise_name, workout_date)
        reps_per_set = prog["reps"]

        # Crear sets (normalmente 3 sets)
        sets = []
        for set_num, reps in enumerate(reps_per_set, 1):
            # 20% de chance de haber llegado a failure en el último set
            reached_failure = set_num == len(reps_per_set) and random.random() < 0.2

            set_log = SetModel(
                set_number=set_num,
                weight=weight,
                reps=reps + random.randint(-2, 2),  # Variación pequeña en reps
                reached_failure=reached_failure,
            )
            sets.append(set_log)

        # Snapshot de músculos
        muscles_snapshot = [
            WorkoutExerciseMuscleModel(name=m.name, involvement=m.involvement)
            for m in exercise_model.muscles
        ]

        # Crear WorkoutExercise
        workout_exercise = WorkoutExerciseModel(
            exercise_name=exercise_name,
            exercise_category=exercise_model.category,
            position=position,
            exercise_id=exercise_model.id,
            sets=sets,
            muscles=muscles_snapshot,
        )
        workout_exercises.append(workout_exercise)

    # Satisfacción e intensidad realistas
    satisfaction = random.choices(
        SATISFACTION_LEVELS, weights=[5, 10, 20, 35, 30]
    )[0]  # Sesgado hacia "good" y "great"
    intensity = random.choices(INTENSITY_LEVELS, weights=[5, 15, 30, 35, 15])[0]

    workout = WorkoutModel(
        date=workout_date.date(),
        satisfaction=satisfaction,
        intensity=intensity,
        workout_exercises=workout_exercises,
    )

    session.add(workout)
    return workout


def generate_workout_dates() -> list[datetime]:
    """Genera fechas de workouts realistas (3-4 veces por semana)."""
    start_date = datetime(2025, 1, 1)
    today = datetime.now()

    dates = []
    current = start_date

    while current <= today:
        # 70% de chance de haber entrenado ese día
        if random.random() < 0.70:
            dates.append(current)

        # Saltamos 1-2 días (descanso)
        current += timedelta(days=random.randint(1, 2))

    return sorted(dates)


def seed_database() -> None:
    """Llena la BD con datos de entrenamientos."""
    try:
        with DBSession() as session:
            print("Creando ejercicios...")
            exercises_map = create_exercises(session)

            print("Generando workouts (2025-2026)...")
            workout_dates = generate_workout_dates()
            print(f"   Total de días con entrenamiento: {len(workout_dates)}")

            for i, workout_date in enumerate(workout_dates, 1):
                create_workout_for_date(session, workout_date, exercises_map)

                if i % 50 == 0:
                    session.commit()
                    print(f"   {i} workouts creados...")

            session.commit()
            print(f"{len(workout_dates)} workouts creados exitosamente")

    except Exception as e:
        print(f"Error al llenar la BD: {e}")
        raise


