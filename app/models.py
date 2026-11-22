from datetime import date, datetime, timezone
from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship, SQLModel


# ==================== User Models ====================
class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, min_length=3, max_length=50)
    email: EmailStr = Field(index=True, unique=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    courses: list["Course"] = Relationship(back_populates="owner", cascade_delete=True)
    study_sessions: list["StudySession"] = Relationship(back_populates="user", cascade_delete=True)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserPublic(UserBase):
    id: int
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==================== Course Models ====================
class CourseBase(SQLModel):
    title: str = Field(min_length=1, max_length=100, index=True)
    description: str | None = None


class Course(CourseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    owner: User | None = Relationship(back_populates="courses")
    study_sessions: list["StudySession"] = Relationship(back_populates="course", cascade_delete=True)


class CourseCreate(CourseBase):
    pass


class CoursePublic(CourseBase):
    id: int
    user_id: int
    created_at: datetime


class CourseUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


# ==================== Study Session Models ====================
class StudySessionBase(SQLModel):
    course_id: int = Field(index=True)
    minutes: int = Field(gt=0, le=1440, description="Minutes studied (1 - 1440)")
    session_date: date = Field(default_factory=date.today, index=True)
    notes: str | None = None


class StudySession(StudySessionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User | None = Relationship(back_populates="study_sessions")
    course: Course | None = Relationship(back_populates="study_sessions")


class StudySessionCreate(StudySessionBase):
    pass


class StudySessionPublic(StudySessionBase):
    id: int
    user_id: int
    created_at: datetime


class StudySessionUpdate(SQLModel):
    course_id: int | None = None
    minutes: int | None = Field(default=None, gt=0, le=1440)
    session_date: date | None = None
    notes: str | None = None


# ==================== Stats Models ====================
class CourseStats(BaseModel):
    course_id: int
    course_title: str
    total_minutes: int
    session_count: int


class StatsResponse(BaseModel):
    total_minutes: int
    total_sessions: int
    weekly_streak: int
    courses: list[CourseStats]
