from typing import Optional, Sequence
from sqlalchemy import select, func
from datetime import date
from sqlalchemy.orm import Session
from infrastructure.database.models.strength_training import (
    WorkoutModel,
    WorkoutExerciseModel,
    WorkoutExerciseMuscleModel,
    SetModel,
    ExerciseModel,
)


class ExerciseNotFoundError(Exception):
    """Raised when a workout references an exercise that doesn't exist in the catalog."""
    pass


class WorkoutRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, workout) -> WorkoutModel:
        workout_exercises = []

        for position, exercise in enumerate(workout.exercises):
            master = self._get_master_exercise(exercise.name)

            if master is None:
                raise ExerciseNotFoundError(f"'{exercise.name}' is not in the exercise catalog. Save it first.")

            sets = [
                SetModel(
                    set_number=i + 1,
                    weight=s.weight,
                    reps=s.reps,
                    reached_failure=s.reached_failure,
                )
                for i, s in enumerate(exercise.sets)
            ]

            muscles_snapshot = [
                WorkoutExerciseMuscleModel(name=m.name, involvement=m.involvement)
                for m in master.muscles
            ]

            workout_exercises.append(
                WorkoutExerciseModel(
                    exercise_name=exercise.name,
                    exercise_category=master.category,
                    position=position,
                    exercise_id=master.id,
                    sets=sets,
                    muscles=muscles_snapshot,
                )
            )

        workout_model = WorkoutModel(
            date=workout.date,
            satisfaction=workout.satisfaction,
            intensity=workout.intensity,
            workout_exercises=workout_exercises,
        )

        self.session.add(workout_model)
        self.session.commit()
        self.session.refresh(workout_model)
        return workout_model

    def _get_master_exercise(self, name: str) -> Optional[ExerciseModel]:
        stmt = select(ExerciseModel).where(ExerciseModel.name == name)
        return self.session.scalars(stmt).first()

    def get_all(self) -> Sequence[WorkoutModel]:
        stmt = select(WorkoutModel)
        return self.session.scalars(stmt).all()
    
    def get_heatmap_data(self, year: str) -> list[dict]:
        year_int = int(year)
        start = date(year_int, 1, 1)
        end = date(year_int + 1, 1, 1)

        stmt = select(
            WorkoutModel.date,
            WorkoutModel.satisfaction,
            WorkoutModel.intensity
        ).where(
            WorkoutModel.date >= start,
            WorkoutModel.date < end
        )

        rows = self.session.execute(stmt).all()
        
        # return [
        #     {
        #         "date": str(row.date),  # "2025-03-15"
        #         "satisfaction": row.satisfaction,
        #         "intensity": row.intensity
        #     }
        #     for row in rows
        # ]
        data = []
        print(f"Loading {year_int} workouts for heatmap")
        for row in rows:
            d = { "date": str(row.date), "satisfaction": row.satisfaction, "intensity": row.intensity }
            print(d)
            data.append(d)
        return data
    
    def get_data_by_category(self, category: str) -> list[dict]:
        stmt = (
            select(
                WorkoutModel.date,
                WorkoutExerciseModel.exercise_name,
                SetModel.set_number,
                SetModel.weight,
                SetModel.reps,
            )
            .join(WorkoutExerciseModel, WorkoutExerciseModel.workout_id == WorkoutModel.id)
            .join(SetModel, SetModel.workout_exercise_id == WorkoutExerciseModel.id)
            .where(WorkoutExerciseModel.exercise_category == category)
            .order_by(
                WorkoutExerciseModel.exercise_name.asc(),
                WorkoutModel.date.asc(),
                SetModel.set_number.asc(),
            )
        )
        rows = self.session.execute(stmt).all()

        return [
            {
                "date": row.date.isoformat(),
                "exercise_name": row.exercise_name,
                "set_number": row.set_number,
                "weight": row.weight,
                "reps": row.reps,
            }
            for row in rows
        ]

        # Example of returned dicc:
        # [
        #     {"date": "2026-06-03", "exercise_name": "bench press", "set_number": 1, "weight": 45.0, "reps": 12},
        #     {"date": "2026-06-03", "exercise_name": "bench press", "set_number": 2, "weight": 40.0, "reps": 12},
        #     {"date": "2026-06-03", "exercise_name": "bench press", "set_number": 3, "weight": 40.0, "reps": 8},
        #     {"date": "2026-06-10", "exercise_name": "bench press", "set_number": 1, "weight": 47.5, "reps": 12},
        #     {"date": "2026-06-10", "exercise_name": "bench press", "set_number": 2, "weight": 42.5, "reps": 10},
        #     {"date": "2026-06-03", "exercise_name": "overhead press", "set_number": 1, "weight": 25.0, "reps": 10},
        # ]
    
