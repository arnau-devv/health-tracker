wrkt = {
    'type': 'save_workout',
    'payload': {
        'date': '2026-08-16T22:00:00.000Z',
        'satisfaction': 'good',
        'intensity': 'high',
        'exercises': [
            {
                'name': 'bench press',
                'sets': [
                    {'weight': 45, 'reps': 12, 'reached_failure': False},
                    {'weight': 40, 'reps': 12, 'reached_failure': False},
                    {'weight': 40, 'reps': 8, 'reached_failure': False},
                ]
            },
            {
                'name': 'pushups',
                'sets': [
                    {'weight': 18, 'reps': 10, 'reached_failure': False},
                    {'weight': 16, 'reps': 10, 'reached_failure': False},
                    {'weight': 14, 'reps': 10, 'reached_failure': False},
                ]
            },
        ]
    }
}
from datetime import datetime

class SetLog:
    def __init__(self, weight: float, reps: int, reached_failure: bool):
        self._weight: int | float = weight
        self._reps: int = reps
        self._reached_failure: bool = reached_failure

    @property
    def weight(self) -> float: return self._weight
    @property
    def reps(self) -> int: return self._reps
    @property
    def reached_failure(self) -> bool: return self._reached_failure

    @staticmethod
    def validate(exercise_name: str, set_data: dict) -> list:
        errors: list = []
        weight: int | float = set_data.get("weight")
        reps: int = set_data.get("reps")
        reached_failure: bool = set_data.get("reached_failure") 
    
        SetLog._validate_weight(weight, errors)
        SetLog._validate_reps(reps, errors)
        SetLog._validate_reached_failure(reached_failure, errors)

        return errors
    
    @staticmethod
    def _validate_weight(weight: float, errors: list) -> None:
        if not isinstance(weight, (int, float)): 
            errors.append("Weight must be a number (integers or decimals only).")
            return
        
        if weight <= 0:
            errors.append("Weight must be greater than 0.")
        if weight > 999:
            errors.append("Weight cannot exceed 999.")
            
    @staticmethod
    def _validate_reps(reps: int, errors: list) -> None:
        if not isinstance(reps, int): 
            errors.append("Weight must be a number (integers only).")
            return
        
        if reps <= 0:
            errors.append("Reps must be greater than 0.")
        if reps > 99:
            errors.append("Reps cannot exceed 99.")
            
    @staticmethod
    def _validate_reached_failure(reached_failure: bool, errors: list) -> None:
        if not isinstance(reached_failure, bool):
            errors.append("Failure status must be true or false.")
            return
        
    @staticmethod
    def _validate_reached_failure(reached_failure: bool, errors: list) -> None:
        if not isinstance(reached_failure, bool):
            errors.append("Failure status must be true or false.")
            return


class WorkoutExercise:
    def __init__(self, name: str, sets: list[SetLog]):
        self._name: str = name.strip().lower()
        self._sets: list[SetLog] = sets

    @property
    def name(self) -> str: return self._name
    @property
    def sets(self) -> list: return self._sets

    @staticmethod
    def validate(exercise_data: dict) -> list:
        """Returns a list of error messages. Empty list = valid."""
        errors: list = []
        raw_name: str = exercise_data.get("name")
        sets: list = exercise_data.get("sets", [])
        
        WorkoutExercise._validate_name(raw_name, errors)
        if isinstance(raw_name, str):
            WorkoutExercise._validate_sets(raw_name, sets, errors)
        else:
            errors.append(f"Invalid exericse name - {raw_name}")

        return errors
    
    @staticmethod
    def _validate_name(name: str, errors: list) -> None:
        if not isinstance(name, str):
            errors.append("Exercise name must be text.")
            return
        
        clean_name: str = name.strip().lower()
        
        if not clean_name or len(clean_name) < 3:
            errors.append("Exercise name must have at least 3 characters.")
            return
                
        if len(clean_name) > 60:
            errors.append("Exercise name can't exceed 60 characters.")
            
    @staticmethod
    def _validate_sets(exercise_name: str, sets: list, errors: list) -> None:
        if not sets:
            errors.append(f"'{exercise_name.strip().capitalize()}' has no sets.")
        
        for i, set_data in enumerate(sets):
            set_errors: list = SetLog.validate(exercise_name, set_data)
            errors.extend([f"{exercise_name.strip().capitalize()} - set {i+1}: {e}" for e in set_errors])
        


class Workout:
    def __init__(self, date: str, satisfaction: str, intensity: str, exercises: list[WorkoutExercise]):
        self._date: str = Workout._string_to_date_object(date)
        self._satisfaction: str = satisfaction.strip().lower()
        self._intensity: str = intensity.strip().lower()
        self._exercises: list[WorkoutExercise] = exercises

    @property
    def date(self) -> str: return self._date
    @property
    def satisfaction(self) -> str: return self._satisfaction
    @property
    def intensity(self) -> str: return self._intensity
    @property
    def exercises(self) -> list: return self._exercises

    @staticmethod
    def validate(workout_data: dict) -> list:
        errors = []

        Workout._validate_date(workout_data["date"], errors)
        Workout._validate_satisfaction(workout_data["satisfaction"], errors)
        Workout._validate_intensity(workout_data["intensity"], errors)
        Workout._validate_exercises(workout_data.get("exercises", []), errors)

        return errors
    
    @staticmethod
    def _validate_date(date: str, errors: list) -> None:
        if not isinstance(date, str): 
            errors.append("Date must be text.")
            return
        
        if not date.strip(): 
            errors.append("Workout date is required.")
            return
        
        try:
            date_object: object[date] = Workout._string_to_date_object(date)
        except (ValueError, AttributeError):
            errors.append("Date format is invalid. Use ISO format (e.g., 2026-08-16T22:00:00.000Z).")
            
    @staticmethod
    def _string_to_date_object(date: str) -> date:
        return datetime.fromisoformat(date.replace('Z', '+00:00')).date()
    
    @staticmethod
    def _validate_satisfaction(satisfaction: str, errors: list) -> None:
        if not isinstance(satisfaction, str):
            errors.append("Satisfaction must be text.")
            return
        
        if not satisfaction.strip():
            errors.append("Workout satisfaction date is required.")
            
        if satisfaction.strip().lower() not in ["terrible", "bad", "neutral", "good", "great"]:
            errors.append(f"Invalid workout satisfaction - {satisfaction.strip().capitalize()}")
            
    @staticmethod
    def _validate_intensity(intensity: str, errors: list) -> None:
        if not isinstance(intensity, str):
            errors.append("Intensity must be text.")
            return

        if not intensity.strip():
            errors.append("Workout intensity date is required.")
                    
        if intensity.strip().lower() not in ["very_low", "low", "moderate", "high", "very_high"]:
            errors.append(f"Invalid workout intensity - {intensity.strip().capitalize()}")
            
    @staticmethod
    def _validate_exercises(exercises: list, errors: list) -> None:
        if not exercises:
            errors.append("Workout must have at least one exercise.")
                
        else: 
            for exercise in exercises:
                errors.extend(WorkoutExercise.validate(exercise))
        