"""
seed_and_test.py

Qué hace:
1. Vacía TODA la base de datos (en orden correcto respetando las FKs).
2. Genera 1 año de entrenamientos realistas (push/pull/legs/core) e inserta
   los datos usando los modelos SQLAlchemy directamente.
3. Para cada categoría: lee los datos con el MISMO repositorio que usa tu
   backend (workout_repo.get_data_by_category), y calcula el
   average_daily_progress "a mano", en Python puro (sin pandas, sin tu clase),
   como referencia independiente ("ground truth").
4. Corre tu pipeline real (load_progress -> compute_category_metrics) sobre
   esos mismos datos, para que compares el print() de tu función contra el
   valor esperado calculado en el paso 3.

⚠️ AJUSTA LOS IMPORTS de las 2 primeras líneas si tus rutas reales difieren
   (nombre del módulo donde vive StrengthTrainingdataLoader, etc.)

Ejecutar desde la raíz del proyecto:
    python seed_and_test.py
"""

import random
from datetime import date, timedelta
from statistics import mean
from collections import defaultdict

from infrastructure.database.database import Session, init_db
from infrastructure.database.models.strength_training import (
    WorkoutModel,
    WorkoutExerciseModel,
    WorkoutExerciseMuscleModel,
    SetModel,
    ExerciseModel,
    ExerciseMuscleModel,
)
from infrastructure.database.repositories.sports.workout_repository import WorkoutRepository

# AJUSTA esta ruta al módulo real donde tienes la clase:
from modules.sports.strength_training.data_loader import StrengthTrainingdataLoader

random.seed(42)  # reproducibilidad: mismos datos cada vez que ejecutes el script


# ════════════════════════════════════════════════════════════════════
# 1. VACIAR LA BASE DE DATOS
# ════════════════════════════════════════════════════════════════════

def wipe_database():
    init_db()  # por si las tablas no existen todavía (create_all suele ser idempotente)
    with Session() as session:
        # orden: hijos antes que padres, para no violar las foreign keys
        session.query(SetModel).delete()
        session.query(WorkoutExerciseMuscleModel).delete()
        session.query(WorkoutExerciseModel).delete()
        session.query(WorkoutModel).delete()
        session.query(ExerciseMuscleModel).delete()
        session.query(ExerciseModel).delete()
        session.commit()
    print("✔ Base de datos vaciada.")


# ════════════════════════════════════════════════════════════════════
# 2. GENERAR Y CARGAR 1 AÑO DE ENTRENOS
# ════════════════════════════════════════════════════════════════════

# rutina semanal: qué categoría se entrena qué día de la semana (0=lunes)
ROUTINE = {
    0: "push",   # lunes
    2: "pull",   # miércoles
    4: "legs",   # viernes
    5: "core",   # sábado
}

EXERCISES_BY_CATEGORY = {
    "push": ["bench press", "overhead press", "pushups"],
    "pull": ["barbell rows", "lat pulldowns", "pull ups"],
    "legs": ["back squat", "leg press", "romanian deadlift"],
    "core": ["cable crunches", "weighted sit ups"],
}

# peso inicial aproximado por ejercicio (algunos "bodyweight" llevan resistencia añadida pequeña
# para evitar baseline = 0, que rompería el % de crecimiento por división entre cero)
START_WEIGHT = {
    "bench press": 40.0, "overhead press": 25.0, "pushups": 5.0,
    "barbell rows": 35.0, "lat pulldowns": 30.0, "pull ups": 5.0,
    "back squat": 50.0, "leg press": 70.0, "romanian deadlift": 45.0,
    "cable crunches": 15.0, "weighted sit ups": 5.0,
}

ADHERENCE = 0.8  # probabilidad de que el usuario SÍ entrene el día que tocaba (simula huecos reales)


def generate_year_of_workouts(start: date, end: date) -> dict:
    """
    Devuelve {category: [ {date, exercise_name, weight, reps} por set ]}
    con progresión realista (tendencia ascendente + ruido semanal).
    """
    current_weight = dict(START_WEIGHT)  # copia mutable, se actualiza semana a semana
    raw_by_category = defaultdict(list)

    day = start
    while day <= end:
        weekday = day.weekday()
        category = ROUTINE.get(weekday)
        if category and random.random() < ADHERENCE:
            for exercise in EXERCISES_BY_CATEGORY[category]:
                # progresión: pequeña subida de tendencia + ruido aleatorio (puede bajar algún día)
                trend = 1.004  # ~0.4% de subida media por sesión
                noise = random.uniform(0.92, 1.08)
                current_weight[exercise] = round(current_weight[exercise] * trend * noise, 2)

                n_sets = random.randint(3, 4)
                for set_number in range(1, n_sets + 1):
                    reps = random.randint(6, 12)
                    # ligera variación de peso entre series del mismo día
                    weight = round(current_weight[exercise] * random.uniform(0.95, 1.0), 2)
                    raw_by_category[category].append({
                        "date": day.isoformat(),
                        "exercise_name": exercise,
                        "set_number": set_number,
                        "weight": weight,
                        "reps": reps,
                    })
        day += timedelta(days=1)

    return raw_by_category


def insert_workouts(raw_by_category: dict):
    with Session() as session:
        # reagrupamos por fecha para crear 1 WorkoutModel por día con sus ejercicios dentro
        by_date = defaultdict(lambda: defaultdict(list))  # date -> exercise_name -> [sets]
        category_of_exercise = {}
        for category, rows in raw_by_category.items():
            for row in rows:
                by_date[row["date"]][row["exercise_name"]].append(row)
                category_of_exercise[row["exercise_name"]] = category

        for date_str, exercises in sorted(by_date.items()):
            workout = WorkoutModel(
                date=date.fromisoformat(date_str),
                satisfaction=random.choice(["bad", "neutral", "greart", "great"]),
                intensity=random.choice(["low", "moderate", "high", "very_low", "very_high"]),
            )
            session.add(workout)
            session.flush()  # para tener workout.id

            for position, (exercise_name, sets) in enumerate(exercises.items(), start=1):
                workout_exercise = WorkoutExerciseModel(
                    exercise_name=exercise_name,
                    exercise_category=category_of_exercise[exercise_name],
                    position=position,
                    workout_id=workout.id,
                    exercise_id=None,  # sin vínculo al catálogo maestro, solo snapshot (válido por schema)
                )
                session.add(workout_exercise)
                session.flush()

                for s in sets:
                    session.add(SetModel(
                        set_number=s["set_number"],
                        weight=s["weight"],
                        reps=s["reps"],
                        reached_failure=random.random() < 0.2,
                        workout_exercise_id=workout_exercise.id,
                    ))

        session.commit()
    print("✔ 1 año de entrenamientos insertado.")


# ════════════════════════════════════════════════════════════════════
# 3. GROUND TRUTH: average_daily_progress calculado a mano (sin pandas)
# ════════════════════════════════════════════════════════════════════

def expected_average_daily_progress(category_raw_data: list[dict]) -> float:
    """
    Replica EXACTAMENTE la misma lógica que tu pipeline (Epley -> media diaria
    por ejercicio -> media diaria MEZCLANDO ejercicios -> % cambio día a día
    -> media de esos %), pero en Python puro, para comparar contra el print()
    real de compute_category_metrics.
    """
    if not category_raw_data:
        return 0.0

    # Paso 1: mismo cálculo que load_progress -> exercise -> date -> day_rm (Epley)
    sets_by_exercise_date = defaultdict(list)
    for row in category_raw_data:
        sets_by_exercise_date[(row["exercise_name"], row["date"])].append(row)

    exercise_date_rm = defaultdict(dict)
    for (exercise, day), sets_ in sets_by_exercise_date.items():
        rms = [s["weight"] * (1 + s["reps"] / 30) for s in sets_]
        exercise_date_rm[exercise][day] = round(sum(rms) / len(rms), 2)

    # Paso 2: mezclar todos los ejercicios por fecha (como groupby("date")["rm"].mean())
    rms_by_date = defaultdict(list)
    for exercise, dates in exercise_date_rm.items():
        for day, rm in dates.items():
            rms_by_date[day].append(rm)

    sorted_dates = sorted(rms_by_date.keys())
    daily_avg = [mean(rms_by_date[d]) for d in sorted_dates]

    # Paso 3: % de cambio día entrenado -> día entrenado siguiente (como pct_change())
    pct_changes = []
    for i in range(1, len(daily_avg)):
        prev, curr = daily_avg[i - 1], daily_avg[i]
        if prev != 0:
            pct_changes.append((curr - prev) / prev * 100)

    if not pct_changes:
        return 0.0
    return round(mean(pct_changes), 2)


# ════════════════════════════════════════════════════════════════════
# 4. ORQUESTADOR
# ════════════════════════════════════════════════════════════════════

def main():
    wipe_database()

    start = date(2025, 1, 1)
    end = date(2025, 12, 31)
    raw_by_category = generate_year_of_workouts(start, end)
    insert_workouts(raw_by_category)

    print()
    print("=" * 60)
    print("COMPARACIÓN: esperado (Python puro) vs. tu pipeline real")
    print("=" * 60)

    with Session() as session:
        workout_repo = WorkoutRepository(session)
        for category in ("push", "pull", "legs", "core"):
            raw_data = workout_repo.get_data_by_category(category)

            expected = expected_average_daily_progress(raw_data)

            processed = StrengthTrainingdataLoader.load_progress(raw_data)
            print(f"\n--- {category} ---")
            print(f"esperado  (calculado aparte): {expected}")
            print("tu función imprime ahora:     ", end="")
            StrengthTrainingdataLoader.compute_category_metrics(processed)  # esto hace el print()


if __name__ == "__main__":
    main()