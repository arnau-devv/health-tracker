from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from infrastructure.database.models.strength_training import ExerciseModel, ExerciseMuscleModel


class ExerciseRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, category: str, bodyweighted: bool, muscles_data: list[dict]) -> ExerciseModel:
        muscles = []
        for muscle_name, involvement in muscles_data.items():
            muscles.append(ExerciseMuscleModel(name = muscle_name, involvement = involvement))
        
        # for muscle in muscles_data:
            # if isinstance (muscle, dict):
            #     muscles.append(ExerciseMuscleModel(name = muscle["name"], involvement = muscle.get("involvement", 1.0)))
            # elif isinstance(muscle, str):
            #     muscles.append(ExerciseMuscleModel(name=muscle, involvement=1.0))
                
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
        stmt = select(ExerciseModel)
        return self.session.scalars(stmt).all()
    
    def get_category_by_name(self, name: str) -> Optional[str]:
        """Devuelve la categoría de un ejercicio por su nombre (ej: 'push', 'pull', 'legs', 'core')."""
        stmt = select(ExerciseModel.category).where(ExerciseModel.name == name)
        return self.session.scalars(stmt).first()
    
    def _get_id_by_name(self, name: str) -> Optional[int]:
        """Devuelve el ID de un ejercicio por su nombre o None si no existe."""
        stmt = select(ExerciseModel.id).where(ExerciseModel.name == name)
        return self.session.scalars(stmt).first()