from typing import Optional, Sequence
from sqlalchemy import select, func
from datetime import date
from sqlalchemy.orm import Session, selectinload
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
        
    def get_data_by_date(self, selected_date: str) -> dict:
        date_for_query = date.fromisoformat(selected_date)
        stmt = (
        select(WorkoutModel)
        .options(
            selectinload(WorkoutModel.workout_exercises)
            .selectinload(WorkoutExerciseModel.sets),
            selectinload(WorkoutModel.workout_exercises)
            .selectinload(WorkoutExerciseModel.exercise),
        )
        .where(WorkoutModel.date == date_for_query)
        .order_by(WorkoutModel.created_at.desc())
        )
        workout = self.session.scalars(stmt).first()

        exercises_data = []

        ordered_exercises = sorted(
            workout.workout_exercises,
            key=lambda workout_exercise: workout_exercise.position
        )

        for workout_exercise in ordered_exercises:
            exercise = workout_exercise.exercise

            sets_data = []

            ordered_sets = sorted(
                workout_exercise.sets,
                key=lambda workout_set: workout_set.set_number
            )

            for workout_set in ordered_sets:
                sets_data.append({
                    "set_number": workout_set.set_number,
                    "weight": workout_set.weight,
                    "reps": workout_set.reps,
                    "reached_failure": workout_set.reached_failure,
                })

            exercises_data.append({
                "name": workout_exercise.exercise_name,
                "bodyweighted": exercise.bodyweighted,
                "sets": sets_data,
            })

        return {
            "date": selected_date,
            "satisfaction": workout.satisfaction,
            "intensity": workout.intensity,
            "exercises": exercises_data,
        }
        
        # Example of returned dicc:
        # {
        #     "date": date(2026, 9, 23), "satisfaction": "good", "intensity": "high",
        #     "exercises": [
        #         {
        #             "name": "bench press", "bodyweighted": False,
        #             "sets": [
        #                 {"set_number": 1, "weight": 45.0, "reps": 12, "reached_failure": False},
        #                 {"set_number": 2, "weight": 40.0, "reps": 8, "reached_failure": True},
        #             ]
        #         },
        #         {
        #             "name": "pushups", "bodyweighted": True,
        #             "sets": [{"set_number": 1, "weight": 18.0, "reps": 15, "reached_failure": False}]
        #         }
        #     ]
        # }
