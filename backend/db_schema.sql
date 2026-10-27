/* ============================ EXERCISES ============================ */
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(4) NOT NULL
        CONSTRAINT check_exercise_category CHECK (category IN ('push', 'pull', 'legs', 'core')),
    bodyweighted BOOLEAN NOT NULL
        CONSTRAINT check_exercise_bodyweighted CHECK (bodyweighted IN (0, 1))
);
/* Live/Master table: Used for current configuration data that can be modified over time.*/
CREATE TABLE IF NOT EXISTS exercise_muscles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    involvement FLOAT NOT NULL
        CONSTRAINT check_muscle_involvement CHECK (involvement > 0 AND involvement <= 1),
    exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE
);

/*  Snapshot table: Used for historical data that cannot be modified 
(ensures dashboard and metrics remain accurate even if exercises change).*/
CREATE TABLE IF NOT EXISTS workout_exercise_muscles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_exercise_id INTEGER NOT NULL REFERENCES workout_exercises(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    involvement FLOAT NOT NULL
        CONSTRAINT check_we_muscle_involvement CHECK (involvement > 0 AND involvement <= 1)
);


/* ============================ WORKOUTS ============================ */
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL DEFAULT (date('now')),
    satisfaction VARCHAR(50) NOT NULL,
    intensity VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE IF NOT EXISTS workout_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
    exercise_id INTEGER REFERENCES exercises(id) ON DELETE SET NULL,
    exercise_name VARCHAR(100) NOT NULL,        -- snapshot del nombre al momento de loggear
    exercise_category VARCHAR(20) NOT NULL,    -- snapshot de la categoría al momento de loggear
    position INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_exercise_id INTEGER NOT NULL REFERENCES workout_exercises(id) ON DELETE CASCADE,
    set_number INTEGER NOT NULL,
    weight FLOAT NOT NULL,
    reps INTEGER NOT NULL,
    reached_failure BOOLEAN NOT NULL
        CONSTRAINT check_set_reached_failure CHECK (reached_failure IN (0, 1))
);
