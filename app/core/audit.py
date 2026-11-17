from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.models import Base, IdMixin

class AuditLog(IdMixin, Base):
    __tablename__ = "audit_log"
    __table_args__ = (Index("ix_audit_entity", "entity", "entity_id", "ts"),)
    
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("app_user.id", ondelete="SET NULL"))
    entity: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    entity_label: Mapped [str | None] = mapped_column(String(120))
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    field: Mapped[str | None] = mapped_column(String(60))
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="web")

    user = relationship("User", lazy="joined")

def _fmt(v:Any) -> str | None:
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return str(v.normalize())
    return str(v)

def record(
    db: Session,
    *,
    user_id: int | None,
    entity: str,
    entity_id: int,
    action: str,
    label: str | None = None,
    field: str | None = None,
    old: Any = None,
    new: Any = None,
    source: str = "web",
) -> None :
    db.add(
        AuditLog(
            user_id=user_id,
            entity=entity,
            entity_id=entity_id,
            entity_label=label,
            action=action,
            field=field,
            old_value=_fmt(old),
            new_value=_fmt(new),
            source=source,
        )
    )

def record_diff(
        db: Session,
        *,
        user_id: int | None,
        entity: str,
        entity_id: int,
        label: str | None,
        before: dict[str, Any],
        after: dict[str, Any],
        display: dict[str,str] | None = None,
        source: str = "web",
) -> int:
    n = 0
    for key, new in after.items():
        old = before.get(key)
        if _fmt(old) == _fmt(new):
            continue
        record(
            db,
            user_id=user_id,
            entity=entity,
            label=label,
            action="update",
            field=(display or {}).get(key, key),
            old=old,
            new=new,
            source=source,
        )
        n += 1
    return n