from sqlalchemy import select
from infrastructure.database.database import engine, Base, Session, init_db
from infrastructure.database.models.strength_training import (
    ExerciseModel, ExerciseMuscleModel, WorkoutModel, 
    WorkoutExerciseModel, WorkoutExerciseMuscleModel, Set
)

def run_tests():
    print("1. Creando tablas en SQLite...")
    init_db()
    print("   ¡Tablas creadas correctamente!")

    with Session() as session:
        # 2. Insertar un ejercicio maestro con sus músculos
        print("\n2. Insertando Ejercicio maestro (Press de Banca)...")
        bench_press = ExerciseModel(
            name="Handstand Pushups",
            category="push",
            bodyweighted=False,
            muscles=[
                ExerciseMuscleModel(name="Chest", involvement=0.7),
                ExerciseMuscleModel(name="Triceps", involvement=0.3),
            ]
        )
        session.add(bench_press)
        session.commit()

        # 3. Registrar un entrenamiento (Workout) usando el ejercicio
        print("3. Registrando un Workout con series y snapshot de músculos...")
        workout = WorkoutModel(
            satisfaction="Great",
            intensity="High",
            workout_exercises=[
                WorkoutExerciseModel(
                    exercise_name=bench_press.name,       # Snapshot del nombre
                    exercise_category=bench_press.category, # Snapshot de categoría
                    position=1,
                    exercise_id=bench_press.id,
                    sets=[
                        Set(set_number=1, weight=80.0, reps=10, reached_failure=False),
                        Set(set_number=2, weight=85.0, reps=8, reached_failure=True),
                    ],
                    muscles=[
                        WorkoutExerciseMuscleModel(name="Chest", involvement=0.7),
                        WorkoutExerciseMuscleModel(name="Triceps", involvement=0.3),
                    ]
                )
            ]
        )
        session.add(workout)
        session.commit()

        # 4. Consultar los datos insertados para validar relaciones
        print("\n4. Consultando los datos desde la base de datos:")
        stmt = select(WorkoutModel).order_by(WorkoutModel.id.desc())
        saved_workout = session.scalars(stmt).first()
        
        print(f"   Workout ID: {saved_workout.id} | Fecha: {saved_workout.date}")
        for we in saved_workout.workout_exercises:
            print(f"   - Ejercicio registrado: {we.exercise_name} ({we.exercise_category})")
            for s in we.sets:
                print(f"     * Serie {s.set_number}: {s.weight}kg x {s.reps} reps (Fallo: {s.reached_failure})")
            for m in we.muscles:
                print(f"     * Músculo impactado: {m.name} ({m.involvement * 100}%)")

if __name__ == "__main__":
    run_tests()