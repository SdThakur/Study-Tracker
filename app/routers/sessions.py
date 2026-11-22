from datetime import date
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select
from app.models import (
    Course,
    StudySession,
    StudySessionCreate,
    StudySessionPublic,
    StudySessionUpdate,
)
from app.security import CurrentUser, SessionDep

router = APIRouter(prefix="/sessions", tags=["study-sessions"])


@router.post("/", response_model=StudySessionPublic, status_code=status.HTTP_201_CREATED)
def create_session(
    session_in: StudySessionCreate,
    current_user: CurrentUser,
    session: SessionDep,
):
    # Verify course exists and belongs to the user
    course = session.get(Course, session_in.course_id)
    if not course or course.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or not owned by user",
        )

    study_session = StudySession.model_validate(session_in, update={"user_id": current_user.id})
    session.add(study_session)
    session.commit()
    session.refresh(study_session)
    return study_session


@router.get("/", response_model=list[StudySessionPublic])
def list_sessions(
    current_user: CurrentUser,
    session: SessionDep,
    course_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    stmt = select(StudySession).where(StudySession.user_id == current_user.id)

    if course_id is not None:
        stmt = stmt.where(StudySession.course_id == course_id)
    if start_date is not None:
        stmt = stmt.where(StudySession.session_date >= start_date)
    if end_date is not None:
        stmt = stmt.where(StudySession.session_date <= end_date)

    stmt = stmt.order_by(StudySession.session_date.desc()).offset(offset).limit(limit)
    return session.exec(stmt).all()


@router.get("/{session_id}", response_model=StudySessionPublic)
def get_session(
    session_id: int,
    current_user: CurrentUser,
    session: SessionDep,
):
    study_session = session.get(StudySession, session_id)
    if not study_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found")
    if study_session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return study_session


@router.patch("/{session_id}", response_model=StudySessionPublic)
def update_session(
    session_id: int,
    data: StudySessionUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    study_session = session.get(StudySession, session_id)
    if not study_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found")
    if study_session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    update_dict = data.model_dump(exclude_unset=True)

    # If updating course_id, verify the new course exists and belongs to user
    if "course_id" in update_dict and update_dict["course_id"] is not None:
        new_course = session.get(Course, update_dict["course_id"])
        if not new_course or new_course.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target course not found or not owned by user",
            )

    study_session.sqlmodel_update(update_dict)
    session.add(study_session)
    session.commit()
    session.refresh(study_session)
    return study_session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    current_user: CurrentUser,
    session: SessionDep,
):
    study_session = session.get(StudySession, session_id)
    if not study_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found")
    if study_session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    session.delete(study_session)
    session.commit()
