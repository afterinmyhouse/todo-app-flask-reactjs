from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from flaskr.db import db


class AuditEventModel(db.Model):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    payload: Mapped[str] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    user = relationship("UserModel")

