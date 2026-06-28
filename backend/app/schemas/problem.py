from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import Difficulty


class TestCaseCreate(BaseModel):
    input: str = ""
    expected_output: str = ""
    is_hidden: bool = True


class TestCaseRead(TestCaseCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProblemCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str
    constraints: str = ""
    difficulty: Difficulty = Difficulty.easy
    time_limit: float = Field(default=2.0, gt=0, le=30)
    memory_limit: int = Field(default=128, ge=16, le=2048)
    tags: str = ""
    explanation: str = ""
    test_cases: list[TestCaseCreate] = Field(default_factory=list)


class ProblemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    constraints: str | None = None
    difficulty: Difficulty | None = None
    time_limit: float | None = None
    memory_limit: int | None = None
    tags: str | None = None
    explanation: str | None = None


class ProblemRead(BaseModel):
    id: int
    title: str
    description: str
    constraints: str
    difficulty: Difficulty
    time_limit: float
    memory_limit: int
    tags: str
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class ProblemDetail(ProblemRead):
    test_cases: list[TestCaseRead] = []
