from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.lookups.categories import CATEGORIES, DEFAULTS
from app.modules.lookups.models import City, LookupItem, Province

def items(db: Session, category: str, include_inactive: bool = False) -> list[LookupItem]:
    q = select(LookupItem).where(LookupItem.category == category)
    if not include_inactive:
        q = q.where(LookupItem.is_active.is_(True))
    return list(db.scalar(q.order_by(LookupItem.sort_order, LookupItem.value)))

def all_options(db:Session) -> dict[str, list[LookupItem]]:
    rows = db.scalar(
        select(LookupItem)
        .where(LookupItem.is_active.is_(True))
        .order_by(LookupItem.sort_order, LookupItem.value)
    )
    out: dict[str, list[LookupItem]] = {c: [] for c in CATEGORIES}
    for R in rows:
        out.setdefault(R.category, []).append(R)
    return out

def get_or_create(db: Session, category: str, value: str, meta: dict | None = None) -> LookupItem:
    value=value.strip()
    item = db.scalar(
        select(LookupItem).where(
            LookupItem.category == category,
            func.lower(LookupItem.value) == value.lower(),
        )
    )
    if item:
        return item
    nxt = db.scalar(
        select(func.coalesce(func.max(LookupItem.sort_order),0)).where(LookupItem.category == category)
    )
    item = LookupItem(category=category, value=value, sort_order=(nxt or 0)+10, meta=meta or {})
    db.add(item)
    db.flush()
    return item

def seed_defaults(db: Session) -> int:
    n = 0
    for cat, vals in DEFAULTS.items():
        for i, (v, meta) in enumerate(vals):
            exists = db.scalar(
                select(LookupItem.id).where(LookupItem.category == cat, LookupItem.value == v)
            )
            if not exists:
                db.add(LookupItem(category=cat, value=v, sort_order=(i+1)*10,meta=meta))
                n+=1
    db.flush()
    return n

def closed_status_ids(db:Session) -> set[int]:
    return {i.id for i in items(db, "issue_status", True) if i.meta.get("closed")}

def provinces(db:Session) -> list[Province]:
    return list(db.scalar(select(Province).order_by(Province.name)))

def province_with_cities(db: Session) -> list[Province]:
    return list(
        db.scalar(select(Province).options(selectinload(Province.cities)).order_by(Province.name))
    )

def cities(db:Session, province_id: int | None) -> list[City]:
    if not province_id:
        return []
    return list(db.scalar(select(City).where(City.province_id == province_id).order_by(City.name)))
