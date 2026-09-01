"""
Seed script — genera un año entero (2025) de workouts realistas de fuerza.

Si la base de datos no tiene ejercicios creados, primero siembra un catálogo
base (push/pull/legs) para poder generar los workouts sobre él.

Colócalo en la raíz del backend (mismo nivel desde el que corre ws_service.py),
ya que reutiliza exactamente los mismos import paths.

Uso:
    python seed_2025_workouts.py

Es idempotente: si lo vuelves a correr, borra primero los workouts de 2025
antes de regenerarlos, así que no se duplican. Los ejercicios base tampoco
se duplican (se comprueba por nombre antes de crear).
"""

import random
from datetime import date, timedelta
from itertools import cycle

from sqlalchemy import delete

from infrastructure.database.database import Session, init_db
from infrastructure.database.models.strength_training import WorkoutModel
from infrastructure.database.repositories.sports.exercise_repository import ExerciseRepository
from infrastructure.database.repositories.sports.workout_repository import WorkoutRepository
from modules.sports.strength_training.workout import Workout, WorkoutExercise, SetLog

random.seed(7)  # resultados reproducibles entre ejecuciones

SATISFACTIONS = ["great", "good", "neutral", "bad", "terrible"]
SATISFACTION_WEIGHTS = [0.30, 0.35, 0.20, 0.10, 0.05]

INTENSITIES = ["very_low", "low", "moderate", "high", "very_high"]
INTENSITY_WEIGHTS = [0.05, 0.15, 0.35, 0.35, 0.10]

# Días de entreno aproximados por semana, según el mes -> le da vida al calendario
MONTH_FREQUENCY = {
    1: 5,   # motivación de año nuevo
    2: 5,
    3: 4,
    4: 3,   # pequeño bajón
    5: 4,
    6: 5,
    7: 2,   # bajón de verano
    8: 3,   # mes de vacaciones
    9: 5,   # vuelta a la rutina
    10: 5,
    11: 4,
    12: 3,  # las fiestas van bajando el ritmo
}

# Tramos de descanso total (vacaciones, navidades)
REST_RANGES = [
    (date(2025, 8, 4), date(2025, 8, 17)),    # 2 semanas de viaje en verano
    (date(2025, 12, 22), date(2026, 1, 1)),   # vacaciones de invierno
]

# Catálogo base de ejercicios — solo se crean si no existen ya (se busca por nombre)
DEFAULT_EXERCISES = {
    "push": [
        ("bench press", False, {"chest": 0.90, "triceps": 0.60, "anterior_shoulder": 0.40}),
        ("overhead press", False, {"anterior_shoulder": 0.85, "lateral_shoulder": 0.50, "triceps": 0.55}),
        ("pushups", True, {"chest": 0.75, "triceps": 0.50, "anterior_shoulder": 0.35}),
    ],
    "pull": [
        ("pull ups", True, {"lats": 0.90, "biceps": 0.55, "upper_back": 0.50}),
        ("barbell rows", False, {"upper_back": 0.80, "lats": 0.60, "rear_deltoid": 0.40, "biceps": 0.35}),
        ("lat pulldowns", False, {"lats": 0.85, "biceps": 0.40, "upper_back": 0.35}),
    ],
    "legs": [
        ("back squat", False, {"quadriceps": 0.90, "glutes": 0.60, "hamstrings": 0.30}),
        ("leg press", False, {"quadriceps": 0.85, "glutes": 0.50, "hamstrings": 0.30}),
        ("romanian deadlift", False, {"hamstrings": 0.85, "glutes": 0.60, "lower_back": 0.40}),
    ],
}


def is_forced_rest(d: date) -> bool:
    return any(start <= d <= end for start, end in REST_RANGES)


def build_calendar() -> list[date]:
    """Decide qué días de 2025 tienen entreno, con rachas y descansos naturales."""
    trained = []
    streak = 0   # días seguidos entrenando
    rested = 0   # días seguidos descansando

    d = date(2025, 1, 1)
    end = date(2025, 12, 31)

    while d <= end:
        if is_forced_rest(d):
            streak = 0
            rested += 1
            d += timedelta(days=1)
            continue

        base_p = MONTH_FREQUENCY[d.month] / 7

        # Menos probable si llevas 2+ días seguidos entrenando,
        # más probable si llevas 2+ días de descanso -> evita el patrón robótico
        if streak >= 2:
            base_p *= 0.4
        if rested >= 2:
            base_p *= 1.6

        if random.random() < min(base_p, 0.9):
            trained.append(d)
            streak += 1
            rested = 0
        else:
            streak = 0
            rested += 1

        d += timedelta(days=1)

    return trained


def seed_default_exercises(session) -> None:
    """Crea el catálogo base de ejercicios si no existe ya (comprobado por nombre)."""
    repo = ExerciseRepository(session)
    created = 0

    for category, exercises in DEFAULT_EXERCISES.items():
        for name, bodyweighted, muscles in exercises:
            if repo.get_by_name(name) is None:
                repo.create(
                    name=name,
                    category=category,
                    bodyweighted=bodyweighted,
                    muscles_data=muscles,
                )
                created += 1

    if created:
        print(f"Sembrados {created} ejercicios base (push/pull/legs).")


def pick_exercises(category: str, catalog: dict[str, dict], count: int) -> list[str]:
    pool = [name for name, data in catalog.items() if data["category"] == category]
    if not pool:
        pool = list(catalog.keys())  # fallback si esa categoría está vacía
    count = min(count, len(pool))
    return random.sample(pool, count)


def random_sets(base_weight: float, progress: float) -> list[SetLog]:
    """3-4 sets, con progresión de peso ligera a lo largo del año (progress 0..1)."""
    n_sets = random.choice([3, 3, 4])
    weight = round(base_weight * (1 + 0.15 * progress), 1)
    reps_base = random.randint(6, 12)

    sets = []
    for i in range(n_sets):
        sets.append(SetLog(
            weight=weight,
            reps=max(4, reps_base - i),  # reps bajan un poco set a set, como en la realidad
            reached_failure=random.random() < 0.2,
        ))
    return sets


def build_workout(d: date, split: str, catalog: dict[str, dict], progress: float) -> Workout:
    exercise_names = pick_exercises(split, catalog, count=random.choice([3, 4]))

    exercises = [
        WorkoutExercise(
            name=name,
            sets=random_sets(base_weight=random.uniform(15, 60), progress=progress),
        )
        for name in exercise_names
    ]

    return Workout(
        date=d.isoformat(),
        satisfaction=random.choices(SATISFACTIONS, weights=SATISFACTION_WEIGHTS)[0],
        intensity=random.choices(INTENSITIES, weights=INTENSITY_WEIGHTS)[0],
        exercises=exercises,
    )


def wipe_existing_2025(session) -> None:
    session.execute(
        delete(WorkoutModel).where(
            WorkoutModel.date >= date(2025, 1, 1),
            WorkoutModel.date < date(2026, 1, 1),
        )
    )
    session.commit()


def main():
    init_db()

    with Session() as session:
        seed_default_exercises(session)
        catalog = ExerciseRepository(session).get_all_as_dict()

    if not catalog:
        print("No hay ejercicios en la base de datos — algo falló al sembrar el catálogo base.")
        return

    with Session() as session:
        wipe_existing_2025(session)

    trained_days = build_calendar()
    print(f"Generando {len(trained_days)} workouts a lo largo de 2025...")

    split_cycle = cycle(["push", "pull", "legs"])
    year_start = date(2025, 1, 1)
    year_days = 365

    saved = 0
    with Session() as session:
        repo = WorkoutRepository(session)
        for d in trained_days:
            split = next(split_cycle)
            progress = (d - year_start).days / year_days
            workout = build_workout(d, split, catalog, progress)
            repo.create(workout)
            saved += 1

    print(f"Listo — {saved} workouts guardados para 2025.")


if __name__ == "__main__":
    main()
