import pandas as pd
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
    def load_progress(raw_data: list[dict]) -> dict[dict]:
        processed_data = {}
        # --- Data organization 
        # Level 1: group by exercises
        for exercise_name, exercise_rows in groupby(raw_data, key=lambda r: r['exercise_name']):
            exercise_rows: list[dict] = list(exercise_rows)  # groupby da un iterador, lo materializamos
            processed_data[exercise_name]: dict[dict] = {}
            
            # Level 2 - Group exercise by date
            for session_date, date_rows in groupby(exercise_rows, key=lambda r: r['date']):
                sets_of_that_day_by_exercise:list[dict] = list(date_rows)
                
                total_day_exercise_RM = [set_data["weight"] * (1 + set_data["reps"] / 30) for set_data in sets_of_that_day_by_exercise]
                day_exercise_RM = sum(total_day_exercise_RM) / len(total_day_exercise_RM)
                # repeated dates? 2 workouts in aday
                processed_data[exercise_name][session_date] = round(day_exercise_RM, 2)  
        
        return processed_data
        
        # processed_data_example = {'back squat': {'2025-01-04': 20.67, '2025-01-08': 21.87, '2025-01-12': 59.41},
        #                           'leg press': {'2025-01-04': 72.15, '2025-01-08': 46.57, '2025-12-16': 27.74},
        #                           'goblet squat': {'2025-01-04': 20.67, '2025-01-08': 21.87, '2025-01-12': 59.41} }
    
    @staticmethod
    def compute_category_metrics(exercise_progress: dict[dict], cat) -> dict:
        rows: list[dict] = [
            {'exercise': exercise, 'date': date, 'rm': rm}
            for exercise, dates in exercise_progress.items()
            for date, rm in dates.items()
        ]

        category_metrics_dataframe = pd.DataFrame(rows)
        category_metrics_dataframe['date'] = pd.to_datetime(category_metrics_dataframe['date'])
        print(f"---------------- {cat.upper()} --------------------")

        # --- AVERAGE DAILY PROGRESS ---
        days_rms = category_metrics_dataframe.groupby("date")["rm"].mean().sort_index()
        daily_rm_change = days_rms.pct_change() * 100
        average_daily_progress = round(float(daily_rm_change.mean()), 2)
        print(f"---------- {average_daily_progress}")
        
        # --- MONTHLY PROGRESS ---
        monthly_avg_rm = category_metrics_dataframe.groupby(
            category_metrics_dataframe["date"].dt.to_period("M")
        )["rm"].mean()
        monthly_progress = (monthly_avg_rm.pct_change() * 100).round(2)
        print(f"---------- {monthly_progress}")

        # --- ACCUMULATED MONTHLY PROGRESS ---
        accumulated_monthly_progress = (
            (monthly_avg_rm - monthly_avg_rm.iloc[0]) / monthly_avg_rm.iloc[0] * 100
        ).round(2)
        accumulated_monthly_progress.iloc[0] = float("nan")  # consistency con monthly_progress
        print(f"---------- {accumulated_monthly_progress}")
        
        # --- Asssemly final result ---
        return {
            "average_daily_progress": average_daily_progress,
            "monthly_progress": StrengthTrainingdataLoader._series_to_json_dict(monthly_progress),
            "accumulated_monthly_progress": StrengthTrainingdataLoader._series_to_json_dict(accumulated_monthly_progress),
        }


    @staticmethod
    def _series_to_json_dict(series: pd.Series) -> dict:
        """Converts a pandas Series (Period index, float values) to a JSON-serializable dict, replacing NaN with None."""
        return {
            str(period): (None if pd.isna(value) else float(value))
            for period, value in series.items()
        }
        
        
    @staticmethod
    def build_general_progress_results(general_progress: dict) -> dict[dict[dict]]:
        # general_progress: {"push": {exercise: dict -> date: key-> rm: value}, "pull": {...}, ...}
        # returns = {'category_name': { 
        #                               'average_daily_progress': value(float), 
        #                               'monthly_progress':  {'year-month': value(float), year-month': value(float), year-month': value(float)},
        #                               'accumulated_monthly_progress': {'year-month': value(float), year-month': value(float), year-month': value(float)} }
        return {
            category: StrengthTrainingdataLoader.compute_category_metrics(exercise_progress, category)
            for category, exercise_progress in general_progress.items()
        }

            