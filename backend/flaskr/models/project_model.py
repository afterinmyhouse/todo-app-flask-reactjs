from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from flaskr.db import db


class ProjectModel(db.Model):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    color: Mapped[str] = mapped_column(String(24), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("UserModel", back_populates="projects")

    tasks = relationship(
        "TaskModel", back_populates="project", cascade="all, delete-orphan"
    )

