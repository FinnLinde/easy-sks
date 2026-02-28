"""SQLAlchemy ORM model for local app users."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class UserRow(Base):
    """Persistent representation of an EasySKS user."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("mobile_number", name="uq_users_mobile_number"),
    )

    # MVP: keep local user ID aligned with Cognito sub to avoid remapping existing
    # scheduling rows created before local user provisioning is introduced.
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    auth_provider: Mapped[str] = mapped_column(String(32), nullable=False)
    auth_provider_user_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mobile_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    mobile_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
