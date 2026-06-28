from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import Verdict


class RunRequest(BaseModel):
    problem_id: int
    language: str = "python"
    source_code: str = Field(min_length=1)


class SubmitRequest(RunRequest):
    pass


class ExecutionCaseResult(BaseModel):
    input: str
    expected_output: str
    actual_output: str
    stderr: str = ""
    status: Verdict
    execution_time: float = 0
    memory: int = 0


class ExecutionResult(BaseModel):
    status: Verdict
    execution_time: float = 0
    memory: int = 0
    cases: list[ExecutionCaseResult] = []


class SubmissionRead(BaseModel):
    id: int
    user_id: int
    problem_id: int
    language: str
    source_code: str
    status: Verdict
    execution_time: float
    memory: int

    model_config = ConfigDict(from_attributes=True)
