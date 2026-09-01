from itertools import groupby
class StrengthTrainingdataLoader():
    
    #  raw_data = [
    #     {"date": "2026-06-03", "exercise_name": "bench press", "set_number": 2, "weight": 40.0, "reps": 12},
    #     {"date": "2026-06-03", "exercise_name": "bench press", "set_number": 3, "weight": 40.0, "reps": 8},
    #     {"date": "2026-06-10", "exercise_name": "bench press", "set_number": 1, "weight": 47.5, "reps": 12},
    #     {"date": "2026-06-10", "exercise_name": "bench press", "set_number": 2, "weight": 42.5, "reps": 10},
    #     {"date": "2026-06-03", "exercise_name": "overhead press", "set_number": 1, "weight": 25.0, "reps": 10}
    # ]

    @staticmethod
    def load_progress(raw_data: list[dict]) -> dict[dict[dict]]:
        processed_data = {}
        # --- Data organization 
        # Level 1: group by exercises
        for exercise_name, exercise_rows in groupby(raw_data, key=lambda r: r['exercise_name']):
            exercise_rows: list[dict] = list(exercise_rows)  # groupby da un iterador, lo materializamos
            processed_data[exercise_name] = {}
            
            # Level 2 - Group exercise by date
            for session_date, date_rows in groupby(exercise_rows, key=lambda r: r['date']):
                sets_of_that_day_by_exercise:list[dict] = list(date_rows)
                
                total_day_exercise_RM = [set_data["weight"] * (1 + set_data["reps"] / 30) for set_data in sets_of_that_day_by_exercise]
                day_exercise_RM = sum(total_day_exercise_RM) / len(total_day_exercise_RM)
                
                processed_data[exercise_name][session_date] = round(day_exercise_RM, 2)  
        
        return processed_data
        
        # --- Results
        # aqui el codigo esta guarro y estoy estancado, debemos trabajar en esto de aqui
        # processed_data_example = {'core': {},
        #                         'legs': {'back squat': {'2025-01-04': 20.67, '2025-01-08': 21.87, '2025-01-12': 59.41},
        #                                 'leg press': {'2025-01-04': 72.15, '2025-01-08': 46.57, '2025-12-16': 27.74}
        #                                 },
        #                         'pull': {'barbell rows': {'2025-01-02': 46.25} }
        #                         }
          
        # esto es lo que necesito pasar al frontend para hacer el grafico  
        # result = {
        #            'category': {
        #                           'average_daily_progress': value(float),
        #                           'monthly_progress':  {'year-month': value(float), 'year-month': value(float), ...},
        #                           'accumulated_monthly_progress': {'year-month': value(float), 'year-month': value(float), ...},
        #                           'average_monthly_progress': value(float),
        #                           'total_progress': value(float) 
        #                        },
        # }
    
    def compute_category_metrics(exercise_progress):
    


            