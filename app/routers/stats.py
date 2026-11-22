from datetime import date, timedelta
from fastapi import APIRouter
from sqlmodel import select
from app.models import Course, CourseStats, StatsResponse, StudySession
from app.security import CurrentUser, SessionDep

router = APIRouter(prefix="/stats", tags=["stats"])


def calculate_weekly_streak(session_dates: list[date]) -> int:
    if not session_dates:
        return 0

    active_weeks = {d.isocalendar()[:2] for d in session_dates}
    today = date.today()

    # Determine whether streak starts this week or last week
    if today.isocalendar()[:2] in active_weeks:
        curr_date = today
    elif (today - timedelta(days=7)).isocalendar()[:2] in active_weeks:
        curr_date = today - timedelta(days=7)
    else:
        return 0

    streak = 0
    while curr_date.isocalendar()[:2] in active_weeks:
        streak += 1
        curr_date -= timedelta(days=7)

    return streak


@router.get("/", response_model=StatsResponse)
def get_stats(
    current_user: CurrentUser,
    session: SessionDep,
):
    courses = session.exec(select(Course).where(Course.user_id == current_user.id)).all()
    sessions = session.exec(select(StudySession).where(StudySession.user_id == current_user.id)).all()

    # Aggregate by course
    course_stats_map: dict[int, dict] = {
        c.id: {"title": c.title, "minutes": 0, "count": 0} for c in courses if c.id is not None
    }

    session_dates: list[date] = []
    total_minutes = 0

    for s in sessions:
        total_minutes += s.minutes
        session_dates.append(s.session_date)
        if s.course_id in course_stats_map:
            course_stats_map[s.course_id]["minutes"] += s.minutes
            course_stats_map[s.course_id]["count"] += 1

    course_stats_list = [
        CourseStats(
            course_id=cid,
            course_title=data["title"],
            total_minutes=data["minutes"],
            session_count=data["count"],
        )
        for cid, data in course_stats_map.items()
    ]

    streak = calculate_weekly_streak(session_dates)

    return StatsResponse(
        total_minutes=total_minutes,
        total_sessions=len(sessions),
        weekly_streak=streak,
        courses=course_stats_list,
    )
