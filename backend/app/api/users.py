from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.config.database import get_db
from app.models.entities import Leaderboard, User
from app.schemas.user import LeaderboardRead, UserRead

router = APIRouter(tags=["Users"])


@router.get("/profile", response_model=UserRead)
def profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/leaderboard", response_model=list[LeaderboardRead])
def leaderboard(db: Session = Depends(get_db)) -> list[LeaderboardRead]:
    rows = (
        db.query(Leaderboard, User)
        .join(User, User.id == Leaderboard.user_id)
        .order_by(Leaderboard.problems_solved.desc(), Leaderboard.score.desc(), Leaderboard.acceptance_rate.desc())
        .limit(100)
        .all()
    )
    return [
        LeaderboardRead(
            user_id=row.Leaderboard.user_id,
            name=row.User.name,
            problems_solved=row.Leaderboard.problems_solved,
            score=row.Leaderboard.score,
            total_submissions=row.Leaderboard.total_submissions,
            acceptance_rate=row.Leaderboard.acceptance_rate,
        )
        for row in rows
    ]
