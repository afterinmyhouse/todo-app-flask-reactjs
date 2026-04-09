from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from flaskr.db import db


class UserPreferenceModel(db.Model):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    user = relationship("UserModel", back_populates="preferences")

    default_project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), nullable=True, index=True
    )
    default_project = relationship("ProjectModel")

    default_task_status: Mapped[str] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

