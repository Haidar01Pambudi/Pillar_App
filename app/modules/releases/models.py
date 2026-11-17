from datetime import date

from sqlalchemy import Boolean as BOOL, ForeignKey, Date, Integer as INT, Numeric, String, Text as TXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base, IdMixin, SoftDeleteMixin as SDM, TimestampMixin as TSM, UserStampMixin as USM

class SoftwareVersion(IdMixin, TSM, Base):
    __tablename__ = "software_version"

    name:           Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    product:        Mapped[str | None] = mapped_column(String(60))
    released_on:    Mapped[date | None] = mapped_column(Date) 
    is_recommended: Mapped[bool] = mapped_column(BOOL, nullable=False, default=False)
    summary:        Mapped[str | None] = mapped_column(TXT)

    notes: Mapped[list["ReleaseNote"]] = relationship(
        back_populates="version",
        primaryjoin="and_(SoftwareVersion.id==ReleaseNote.version_id, ReleaseNote.deleted_at.is_(None))",
        order_by="ReleaseNote.created_at.desc()",
        viewonly=True,
    )

    def __str__(self):
        return self.name

class ReleaseNote(IdMixin, TSM, USM, SDM, Base):
    __tablename__ = "release_note"

    version_id: Mapped[int] = mapped_column(
        ForeignKey("software_version.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind_id: Mapped[int | None] = mapped_column(ForeignKey("lookup_item.id", ondelete="RESTRICT")) 
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(TXT, nullable=False, default="")

    version: Mapped[SoftwareVersion] = relationship()
    kind = relationship("LookupItem")
    author = relationship("User", foreign_keys="ReleaseNote.created_by_id")