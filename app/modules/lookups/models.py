from decimal import Decimal as DC

from sqlalchemy import Boolean as BOOL, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base, IdMixin

class LookupItem(IdMixin, Base):
    __tablename__ = "lookup_item"
    __table_args__ = (UniqueConstraint("category", "value", name="uq_lookup_item_category_value"),)

    category:   Mapped[str] = mapped_column(String(40), nullable= False, index=True)
    value:      Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[str] = mapped_column(Integer, nullable=False, default=0)
    is_active:  Mapped[str] = mapped_column(BOOL, nullable=False, default=True)
    meta:   Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")

    def __str__(self) -> str:
        return self.value

class Province(IdMixin, Base):
    __tablename__="province"

    name        : Mapped[str]           = mapped_column(String(80), unique=True, nullable=False)  
    country     : Mapped[str]           = mapped_column(String(60), nullable=False, default="Indonesia")
    map_name    : Mapped[str | None]    = mapped_column(String(80))
    cities      : Mapped[list["City"]]  = relationship(back_populates="province", order_by="City.name")

    def __str__(self) -> str:
        return self.name

class City(IdMixin, Base):
    __tablename__ = "city"
    __table_args__ = (UniqueConstraint("province_id", "name", name="uq_city_province_name"),)

    province_id: Mapped[int] = mapped_column(
        ForeignKey("province.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    name:       Mapped[str] = mapped_column(String(120), nullable=False)
    latitute:   Mapped[DC | None] = mapped_column(Numeric(9,6))
    longitude:  Mapped[DC | None] = mapped_column(Numeric(9,6))

    province: Mapped[Province] = relationship(back_populates="cities")

    def __str__(self) -> str:
        return self.name