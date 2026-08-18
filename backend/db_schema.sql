/* ============================ EXERCISES ============================ */
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL CHECK (category IN ('push', 'pull', 'legs', 'core')),
    bodyweighted INTEGER NOT NULL DEFAULT 0 CHECK (bodyweighted IN (0,1))
);
/* Live/Master table: Used for current configuration data that can be modified over time.*/
CREATE TABLE IF NOT EXISTS exercise_muscles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER REFERENCES exercises(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    involvement REAL NOT NULL CHECK (involvement > 0 AND involvement <= 1),
    UNIQUE (exercise_id, name)
);

/*  Snapshot table: Used for historical data that cannot be modified 
(ensures dashboard and metrics remain accurate even if exercises change).*/
CREATE TABLE IF NOT EXISTS workout_exercise_muscles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_exercise_id INTEGER NOT NULL REFERENCES workout_exercises(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    involvement REAL NOT NULL CHECK (involvement > 0 AND involvement <= 1),
    UNIQUE (workout_exercise_id, name)
);


/* ============================ WORKOUTS ============================ */
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL DEFAULT (date('now')),
    satisfaction TEXT NOT NULL,
    intensity TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS workout_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
    exercise_id INTEGER REFERENCES exercises(id) ON DELETE SET NULL,
    exercise_name TEXT NOT NULL,        -- snapshot del nombre al momento de loggear
    exercise_category TEXT NOT NULL,    -- snapshot de la categoría al momento de loggear
    position INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_exercise_id INTEGER NOT NULL REFERENCES workout_exercises(id) ON DELETE CASCADE,
    set_number INTEGER NOT NULL,
    weight REAL NOT NULL,
    reps INTEGER NOT NULL,
    reached_failure INTEGER NOT NULL DEFAULT 0 CHECK (reached_failure IN (0,1))
);
