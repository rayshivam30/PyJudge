from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class Difficulty(str, enum.Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"


class Verdict(str, enum.Enum):
    pending = "Pending"
    accepted = "Accepted"
    wrong_answer = "Wrong Answer"
    compilation_error = "Compilation Error"
    runtime_error = "Runtime Error"
    time_limit_exceeded = "Time Limit Exceeded"
    memory_limit_exceeded = "Memory Limit Exceeded"
    presentation_error = "Presentation Error"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column(Integer, default=1200)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    submissions: Mapped[list["Submission"]] = relationship(back_populates="user")
    leaderboard: Mapped["Leaderboard | None"] = relationship(back_populates="user")


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text)
    constraints: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), default=Difficulty.easy)
    time_limit: Mapped[float] = mapped_column(Float, default=2.0)
    memory_limit: Mapped[int] = mapped_column(Integer, default=128)
    tags: Mapped[str] = mapped_column(String(500), default="")
    explanation: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="problem", cascade="all, delete-orphan")
    submissions: Mapped[list["Submission"]] = relationship(back_populates="problem")


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"))
    input: Mapped[str] = mapped_column(Text, default="")
    expected_output: Mapped[str] = mapped_column(Text, default="")
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=True)

    problem: Mapped[Problem] = relationship(back_populates="test_cases")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"))
    language: Mapped[str] = mapped_column(String(40), default="python")
    source_code: Mapped[str] = mapped_column(Text)
    status: Mapped[Verdict] = mapped_column(Enum(Verdict), default=Verdict.pending)
    execution_time: Mapped[float] = mapped_column(Float, default=0)
    memory: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="submissions")
    problem: Mapped[Problem] = relationship(back_populates="submissions")


class Leaderboard(Base):
    __tablename__ = "leaderboard"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    problems_solved: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[int] = mapped_column(Integer, default=0)
    total_submissions: Mapped[int] = mapped_column(Integer, default=0)
    acceptance_rate: Mapped[float] = mapped_column(Float, default=0)

    user: Mapped[User] = relationship(back_populates="leaderboard")
