from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import *

class IssueCounter(Base):
    __tablename__ = "issue_counter"

    year: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    last_no: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

class Issue(IdMixin, TimestampMixin, UserStampMixin, SoftDeleteMixin, Base):
    __tablename__= ("issue")
    __table_args__= (
        CheckConstraint("closed_date IS NULL OR closed_date >= issue_date", name="closed_after_open"),
    )

    key: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    system_id: Mapped[int] = mapped_column(ForeignKey("system.id", ondelete="RESTRICT"), nullable=False, index=True)

    tittle: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    closed_date: Mapped[date] = mapped_column(Date)

    status_id: Mapped[int] = mapped_column(
        ForeignKey("lookup_item.id", ondelete="RESTRICT"),
        nullable = False,
        index = True
    )

    category_id: Mapped[int | None] = mapped_column(ForeignKey("lookup_item.id", ondelete="RESTRICT"), index=True)
    priority_id: Mapped[int | None] = mapped_column(ForeignKey("lookup_item.id", ondelete="RESTRICT"), index=True)

    pic_id: Mapped[int | None] = mapped_column(ForeignKey("app_user.id", ondelete="SET NULL"), index=True)

    previous_system_status_id: Mapped[int | None] = mapped_column(ForeignKey("lookup_item.id", ondelete="RESTRICT")) 
    current_system_status_id: Mapped[int | None] = mapped_column(ForeignKey("lookup_item.id", ondelete="RESTRICT"))

    sw_version_id: Mapped[int | None] = mapped_column(ForeignKey("software_version.id", ondelete="RESTRICT"))
    fixed_in_version_id: Mapped[int | None] = mapped_column(ForeignKey("software_version.id", ondelete="RESTRICT"))

    action_taken: Mapped[str | None] = mapped_column(Text)
    remarks: Mapped[str | None] = mapped_column(Text)
    documentation_url: Mapped[str | None] = mapped_column(String(1000))

    system = relationship("System", lazy="joined")
    status = relationship("LookupItem", foreign_keys=[status_id], lazy="joined")
    category = relationship("LookupItem", foreign_keys=[category_id], lazy="joined")
    priority = relationship("LookupItem", foreign_keys=[priority_id], lazy="joined")
    previous_system_status = relationship("LookupItem", foreign_keys=[previous_system_status_id], lazy="joined")
    current_system_status = relationship("LookupItem", foreign_keys=[current_system_status_id], lazy="joined")
    pic = relationship("User", foreign_keys=[pic_id], lazy="joined")
    sw_version = relationship("SoftwareVersion", foreign_keys=[sw_version_id], lazy="joined")
    fixed_in_version = relationship("SoftwareVersion", foreign_keys=[fixed_in_version_id])
    comments: Mapped[list["IssueComment"]] = relationship(
        back_populates="issue", order_by="IssueComment.created_at"
    )
    
    @property
    def is_closed(self) -> bool:
        return bool(self.status and self.status.meta.get("closed"))

    @property
    def days_open(self) -> int:
        end = self.closed_date or date.today()
        return (end-self.issue_date).days

    @property
    def age_bucket(self) -> str | None:
        if self.is_closed:
            return None
        d = (date.today() - self.issue_date).days
        return "0-7 d" if d <= 7 else "8-30 d" if d <= 30 else "31-90 d" if d <= 90 else ">90 d" 

class IssueComment(IdMixin, TimestampMixin, Base):
    __tablename__ = "issue_comment"

    issue_id: Mapped[int] = mapped_column(ForeignKey("issue.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("app_user.id", ondelete="SET NULL"))
    body: Mapped[str] = mapped_column(Text,nullable=True)

    issue: Mapped[Issue] = relationship(back_populates="comments")
    author = relationship("User", lazy="joined")