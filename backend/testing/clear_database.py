"""
Función para vaciar completamente la base de datos.
Elimina todos los registros de todas las tablas de strength training.
"""

from sqlalchemy.orm import Session
from infrastructure.database.models.strength_training import (
    SetModel,
    WorkoutExerciseMuscleModel,
    WorkoutExerciseModel,
    WorkoutModel,
    ExerciseMuscleModel,
    ExerciseModel,
)


def clear_all_database(session: Session) -> None:
    """
    Elimina todos los registros de la base de datos de strength training.
    El orden es importante por las foreign keys.
    """
    try:
        # Orden: de lo más específico a lo más general (respetando FKs)
        session.query(SetModel).delete()
        session.query(WorkoutExerciseMuscleModel).delete()
        session.query(WorkoutExerciseModel).delete()
        session.query(WorkoutModel).delete()
        session.query(ExerciseMuscleModel).delete()
        session.query(ExerciseModel).delete()
        
        session.commit()
        print("Base de datos vaciada correctamente")
    except Exception as e:
        session.rollback()
        print(f"Error al vaciar la base de datos: {e}")
        raise


# USO EN TU MAIN:
# from infrastructure.database.database import Session
# from testing.clear_database import clear_all_database
#
# with Session() as session:
#     clear_all_database(session)
