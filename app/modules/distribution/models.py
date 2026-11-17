from datetime import date

from sqlalchemy import Boolean as BOOL, CheckConstraint, Date, ForeignKey, Index, Integer, SmallInteger, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base, IdMixin, SoftDeleteMixin, TimestampMixin, UserStampMixin

def _lookup_fk() -> Mapped[int | None]:
    return mapped_column(ForeignKey("lookup_item.id", ondelete="RESTRICT"), index=True)

class System(IdMixin, TimestampMixin, UserStampMixin, SoftDeleteMixin, Base):
    __tablename__ = "system"
    __table_args__=(
        Index("uq_system_serial_live", "serial_number", unique=True, postgresql_where=text("deleted_at IS NULL")),
        Index(
            "ix_system_serial_trgm",
            "serial_number",
            postgresql_using="gin",
            postgresql_ops={"serial_number":"gin_trgm_ops"},
        ),
        CheckConstraint("bts_count IS NULL OR bts_count >= 0", name="bts_nonneg"),
        CheckConstraint("project_year IS NULL OR project_year BETWEEN 2000 AND 2100", name="year_range"),
    )

    #Identity
    serial_number: Mapped[str] = mapped_column(String(60), nullable=False)
    contract_name: Mapped[str | None] = mapped_column(String(300))
    brand_name: Mapped[str | None] = mapped_column(String(100))
    project_name: Mapped[str | None] = mapped_column(String(300))
    project_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    #Location
    province_id: Mapped[int | None] = mapped_column(ForeignKey("province.id", ondelete="RESTRICT"), index=True) 
    city_id: Mapped[int | None] = mapped_column(ForeignKey("city.id", ondelete="RESTRICT"), index=True)

    #Customer
    customer_id: Mapped[int | None] = _lookup_fk()
    customer_division: Mapped[str] = mapped_column(String(150))
    customer_detail: Mapped[str | None] = mapped_column(String(200))

    #Configuration
    system_type_id: Mapped[int | None] = _lookup_fk()
    antenna_position_id: Mapped[int | None] = _lookup_fk()
    sw_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("software_version.id", ondelete="RESTRICT"), index=True
    )
    server_id: Mapped[int | None] = _lookup_fk()
    interception_Module: Mapped[bool | None] = mapped_column(BOOL)
    bts_count: Mapped[int | None] = mapped_column(Integer)

    #Status
    status_id: Mapped[int | None] = _lookup_fk()
    hardware_status: Mapped[int | None] = mapped_column(String(700))

    #Mileastones
    date_arrive_jakarta: Mapped[date | None] = mapped_column(Date)
    material_check_date: Mapped[date | None] = mapped_column(Date)
    inspection_start: Mapped[date | None] = mapped_column(Date)
    inspection_end: Mapped[date | None] = mapped_column(Date)
    SAT_start: Mapped[date | None] = mapped_column(Date)
    SAT_end: Mapped[date | None] = mapped_column(Date)
    training_start: Mapped[date | None] = mapped_column(Date)
    training_end: Mapped[date | None] = mapped_column(Date)
    regional_training_start: Mapped[date | None] = mapped_column(Date)
    regional_training_end: Mapped[date | None] = mapped_column(Date)
    delivery_date: Mapped[date | None] = mapped_column(Date)

    #Contract/Notes
    contact_person: Mapped[str | None] = mapped_column(String(150))
    remarks: Mapped[str | None] = mapped_column(Text)

    #Data Quailty
    need_review : Mapped[bool] = mapped_column(BOOL, nullable=True, default=False)
    review_note : Mapped[str | None] = mapped_column(Text)

    province = relationship("Province", lazy="joined")
    city = relationship("City", lazy="joined")
    customer = relationship("LookupItem", foreign_keys=[customer_id], lazy="joined")
    system_type = relationship("LookupItem", foreign_keys=[system_type_id], lazy="joined")
    antenna_position = relationship("LookupItem", foreign_keys=[antenna_position_id], lazy="joined")
    server = relationship("LookupItem", foreign_keys=[server_id], lazy="joined")
    status = relationship("LookupItem", foreign_keys=[status_id], lazy="joined")
    sw_version = relationship("SoftwareVersion", lazy="joined")

    def __str__(self) -> str:
        return self.serial_number
