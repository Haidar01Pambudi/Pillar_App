from datetime import datetime as dt
from sqlalchemy import Boolean as BOOL, DateTime as DT, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base, IdMixin, TimestampMixin
from app.core.permissions import Role

class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "app_user"
    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=Role.VIEWER.value)
    is_active: Mapped[bool] = mapped_column(BOOL, nullable=False, default=True)
    last_login_at: Mapped[dt | None] = mapped_column(DT(timezone=True))

def __str__(self) -> str:
    return self.full_name or self.username
