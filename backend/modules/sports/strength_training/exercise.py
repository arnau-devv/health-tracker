
# --- Data recieved from frontend --- 
# exercise = { 
#             type: save_exercise, 
#             payload: {
#                       'name': 'Pushups', 
#                       'muscles': {
#                                   'chest': 0.7, 
#                                   'anterior_shoulder': 0.1, 
#                                   'triceps': 0.2
#                                  }
#                       }
#            }

class Exercise():
    AVAILABLE_EXERCISES = ["bench press", "squat", "deadlift"]
    
    VALID_MUSCLES: frozenset[str] = frozenset({
        # Push
        "chest", "anterior_shoulder", "lateral_shoulder", "triceps", "forearm_extensors",
        # Pull
        "lats", "upper_back", "rear_deltoid", "biceps", "forearm_flexors",
        # Legs
        "quadriceps", "hamstrings", "glutes", "calves", "adductors",
        # Core
        "rectus_abdominis", "obliques", "lower_back",
    })
    
    MUSCLE_CATEGORY: dict[str, str] = {
        # Push
        "chest": "push", "anterior_shoulder": "push", "lateral_shoulder": "push",
        "triceps": "push", "forearm_extensors": "push",
        # Pull
        "lats": "pull", "upper_back": "pull", "rear_deltoid": "pull",
        "biceps": "pull", "forearm_flexors": "pull",
        # Legs
        "quadriceps": "legs", "hamstrings": "legs", "glutes": "legs",
        "calves": "legs", "adductors": "legs",
        # Core
        "rectus_abdominis": "core", "obliques": "core", "lower_back": "core",
    }
    
    def __init__(self, name: str, muscles: dict, bodyweighted: bool):
        self._name: str = name.strip().lower()
        self._muscles: dict[str, float] = { muscle.strip().lower(): intensity for muscle, intensity in muscles.items() }
        self._bodyweighted: bool = bodyweighted
        self._category: str = self._classify(self._muscles)

    @property 
    def name(self) -> str: return self._name    
    @property
    def muscles(self) -> dict: return self._muscles
    @property
    def bodyweighted(self) -> str: return self._bodyweighted
    @property
    def category(self) -> str: return self._category

    # ------------------------- DATA VALIDATION -> raw data from frontend
    @staticmethod
    def validate(exercise_data: dict) -> list:
        """Returns a list of error messages. Empty list = valid."""
        errors = []
        raw_name: str = exercise_data.get("name", "")
        muscles: dict = exercise_data.get("muscles", {})
        bodyweighted: bool = exercise_data.get("bodyweighted", False)
        
        Exercise._validate_name(raw_name, errors)        
        Exercise._validate_muscles(muscles, errors)
        Exercise._validate_bodyweighted(bodyweighted, errors)
        
        return errors
        
    @staticmethod
    def _validate_name(name: str, errors: list) -> None:
        if not isinstance(name, str):
            errors.append("Exercise name must be text.")
            return
        
        clean_name = name.strip().lower()
        
        if not clean_name or len(clean_name) < 3:
            errors.append("Exercise name must have at least 3 characters.")
            return
        
        if len(clean_name) > 60:
            errors.append("Exercise name can't exceed 60 characters.")
            
    @staticmethod
    def _validate_muscles(muscles: dict, errors: list) -> None:
        if not isinstance(muscles, dict):
            errors.append("Muscles must be a dictionary.")
            return
        
        if not muscles:
            errors.append("At least one muscle must be specified.")
            return
        
        elif len(muscles) > 10:
            errors.append("You cannot select more than 10 muscles.")
            return
        
        for muscle, intensity in muscles.items():
            if muscle.strip().lower() not in Exercise.VALID_MUSCLES:
                errors.append(f"Invalid muscle: {muscle}")
            
            if muscle.strip().lower() in Exercise.VALID_MUSCLES and not (0 <= intensity <= 1):
                errors.append(f"Intensity for muscle '{muscle}' must be between 0 and 1.")
        
        return
    
    @staticmethod
    def _validate_bodyweighted(bodyweighted: bool, errors: list) -> None:
        if not isinstance(bodyweighted, bool):
            errors.append("Bodyweighted field must be true or false.")
        
    # ------------------------- UTILITY METHODS ->
    @classmethod
    def _classify(cls, muscles: dict[str, float]) -> str:
        """Sums intensity per category and returns the dominant one."""
        totals: dict[str, float] = {"push": 0.0, "pull": 0.0, "legs": 0.0, "core": 0.0}

        for muscle, intensity in muscles.items():
            category = cls.MUSCLE_CATEGORY.get(muscle)
            if category:
                totals[category] += intensity

        return max(totals, key=totals.get)
        
    @classmethod
    def get_instance_by_name(cls, name: str) -> object:
        clean_name = name.strip().lower()
        
        if clean_name not in cls.AVAILABLE_EXERCISES:
            raise ValueError(f"Exercise '{name}' is not available.")

        # return cls(name=clean_name,) 
        ...
    