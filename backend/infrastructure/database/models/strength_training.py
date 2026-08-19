from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Enum, Float,
    ForeignKey, Integer, String, Date, Text, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from infrastructure.database.database import Base


# ════════════════════════════════════════════════════════════════════
#  EXERCISES
# ════════════════════════════════════════════════════════════════════

class ExerciseModel(Base):
    __tablename__ = "exercises"
    __table_args__ = (
        CheckConstraint("category IN ('push','pull','legs','core')", name="check_exercise_category"),
        CheckConstraint("bodyweighted IN (0,1)", name="check_exercise_bodyweighted"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(
        Enum("push", "pull", "legs", "core"), nullable=False
    )
    bodyweighted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    muscles: Mapped[list["ExerciseMuscleModel"]] = relationship(
        back_populates="exercise", cascade="all, delete-orphan"
    )
    workout_exercises: Mapped[list["WorkoutExerciseModel"]] = relationship(
        back_populates="exercise"
    )


class ExerciseMuscleModel(Base):
    """Live muscle involvement data — editable, linked to the master exercise."""
    __tablename__ = "exercise_muscles"
    __table_args__ = (
        CheckConstraint("involvement > 0 AND involvement <= 1", name="check_muscle_involvement"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    involvement: Mapped[float] = mapped_column(Float, nullable=False)

    # FK → exercises
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    exercise: Mapped["ExerciseModel"] = relationship(back_populates="muscles")


# ════════════════════════════════════════════════════════════════════
#  WORKOUTS
# ════════════════════════════════════════════════════════════════════

class WorkoutModel(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=func.date("now"))
    satisfaction: Mapped[str] = mapped_column(String(50), nullable=False)
    intensity: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relationships
    workout_exercises: Mapped[list["WorkoutExerciseModel"]] = relationship(
        back_populates="workout", cascade="all, delete-orphan"
    )


class WorkoutExerciseModel(Base):
    """
    Bridge between a workout and an exercise.
    Snapshots name and category at log time — metrics stay accurate even if the
    master exercise is later edited or deleted.
    """
    __tablename__ = "workout_exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exercise_name: Mapped[str] = mapped_column(String(100), nullable=False)     # snapshot
    exercise_category: Mapped[str] = mapped_column(String(20), nullable=False)  # snapshot
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    # FK → workouts (hard delete)
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    workout: Mapped["WorkoutModel"] = relationship(back_populates="workout_exercises")

    # FK → exercises (soft delete — SET NULL keeps the snapshot intact)
    exercise_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("exercises.id", ondelete="SET NULL"), nullable=True
    )
    exercise: Mapped[Optional["ExerciseModel"]] = relationship(back_populates="workout_exercises")

    # Relationships
    sets: Mapped[list["SetModel"]] = relationship(
        back_populates="workout_exercise", cascade="all, delete-orphan"
    )
    muscles: Mapped[list["WorkoutExerciseMuscleModel"]] = relationship(
        back_populates="workout_exercise", cascade="all, delete-orphan"
    )


class WorkoutExerciseMuscleModel(Base):
    """
    Snapshot of muscle involvement at log time.
    Decoupled from exercise_muscles — historical data is never altered.
    """
    __tablename__ = "workout_exercise_muscles"
    __table_args__ = (
        CheckConstraint("involvement > 0 AND involvement <= 1", name="check_we_muscle_involvement"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    involvement: Mapped[float] = mapped_column(Float, nullable=False)

    # FK → workout_exercises
    workout_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercises.id", ondelete="CASCADE"), nullable=False
    )
    workout_exercise: Mapped["WorkoutExerciseModel"] = relationship(back_populates="muscles")


class SetModel(Base):
    __tablename__ = "sets"
    __table_args__ = (
        CheckConstraint("reached_failure IN (0,1)", name="check_set_reached_failure"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    reached_failure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # FK → workout_exercises
    workout_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercises.id", ondelete="CASCADE"), nullable=False
    )
    workout_exercise: Mapped["WorkoutExerciseModel"] = relationship(back_populates="sets")