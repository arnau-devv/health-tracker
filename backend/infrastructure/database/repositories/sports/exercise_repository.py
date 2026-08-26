from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from infrastructure.database.models.strength_training import ExerciseModel, ExerciseMuscleModel


class ExerciseRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, category: str, bodyweighted: bool, muscles_data: list[dict]) -> ExerciseModel:
        muscles = []
        for muscle_name, involvement in muscles_data.items():
            muscles.append(ExerciseMuscleModel(name = muscle_name, involvement = involvement))
                
        exercise = ExerciseModel(
            name=name,
            category=category,
            bodyweighted=bodyweighted,
            muscles = muscles
        )
        self.session.add(exercise)
        self.session.commit()
        self.session.refresh(exercise)
        return exercise

    def get_by_name(self, name: str) -> Optional[ExerciseModel]:
        stmt = select(ExerciseModel).where(ExerciseModel.name == name)
        return self.session.scalars(stmt).first()


    def get_all(self) -> Sequence[ExerciseModel]:
        stmt = select(ExerciseModel).options(selectinload(ExerciseModel.muscles))
        return self.session.scalars(stmt).all()
    
    def get_category_by_name(self, name: str) -> Optional[str]:
        """Devuelve la categoría de un ejercicio por su nombre (ej: 'push', 'pull', 'legs', 'core')."""
        stmt = select(ExerciseModel.category).where(ExerciseModel.name == name)
        return self.session.scalars(stmt).first()
    
    def _get_id_by_name(self, name: str) -> Optional[int]:
        """Devuelve el ID de un ejercicio por su nombre o None si no existe."""
        stmt = select(ExerciseModel.id).where(ExerciseModel.name == name)
        return self.session.scalars(stmt).first()
    
    
    def get_all_as_dict(self) -> dict[str, dict]:
        exercises: Sequence[ExerciseModel] = self.get_all()

        result: dict[str, dict] = {}

        for exercise in exercises:
            muscles_dict = {
                muscle.name: muscle.involvement
                for muscle in exercise.muscles
            }

            result[exercise.name] = {
                "name": exercise.name,
                "category": exercise.category,
                "muscles": muscles_dict,
            }

        # {
        #     "bench press": {
        #         "name": "bench press",
        #         "category": "push",
        #         "muscles": {
        #             "chest": 0.9,
        #             "triceps": 0.6,
        #             "front delts": 0.4
        #         }
        #     },
        #     "squat": {
        #         "name": "squat",
        #         "category": "legs",
        #         "muscles": {
        #             "quads": 0.9,
        #             "glutes": 0.7
        #         }
        #     }
        # }
        return result