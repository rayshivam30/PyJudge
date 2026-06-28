from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    rating: int
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class LeaderboardRead(BaseModel):
    user_id: int
    name: str
    problems_solved: int
    score: int
    total_submissions: int
    acceptance_rate: float
