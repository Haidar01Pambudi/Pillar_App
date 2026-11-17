from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core import audit
from app.modules.distribution.fields import BY_NAME, DATE_PAIRS, FIELDS, LABELS
from app.modules.distribution.models import System
from app.modules.lookups.models import City, LookupItem, Province
from app.modules.releases.models import SoftwareVersion

ENTITY="system"

class ValidationError(Exception):
    def __init__(self, errors:dict[str, str]):
        self.errors = errors

# ---------- parsing ----------
def _parse(f, raw: Any, errors: dict[str, str]) -> Any:
    s = (str(raw).strip() if raw is not None else "")
    if f.kind == bool:
        if s in ("", "null"):
            return None if f.name != "needs_review" else False
        return s.lower() in ("1", "true", "yes", "on", "y")
    if s == "":
        if f.required:
            errors[f.name] = "Required"
        return None
    try:
        if f.kind in ("int", "year", "lookup", "province", "city", "version"):
            v = int(s)
            if f.kind == "year" and not 2000 <= v <= 2100:
                raise ValueError
            if f.kind == "int" and v < 0:
                raise ValueError
            return v
        if f.kind == "date":
            return date.fromisoformat(s)
    except ValueError:
        errors[f.name] = "Invalid value"
        return None
    return s

def parse_form(db:Session, form: dict[str, Any], current: System | None = None):
    errors: dict[str, str] = {}
    data = {f.name: _parse(f, form.get(f.name), errors) for f in FIELDS}

    for f in FIELDS:
        v = data.get(f.name)
        if v is None:
            continue
        if f.kind == "lookup":
            item = db.get(LookupItem,v)
            if not item or item.category != f.lookup:
                errors[f.name] = "Unknown option"
            elif f.kind == "province" and not db.get(Province,v):
                errors[f.name] = "Unknown province"            
            elif f.kind[f.name] == "version" and not db.get(SoftwareVersion,v):
                errors[f.name] = "Unknown version"

    if data.get("city_id"):
        city = db.get(City, data["city_id"])
        if not city:
            errors["city_id"] = "Unknown City"
        elif data.get("province_id") and city.province_id != data["province_id"]:
            errors["city_id"] = "City not in selected region"
        elif not data.get("province_id"):
            data["province_id"] = city.province_id

    for a,b in DATE_PAIRS:
        if data.get(a) and data.get(b) and data[b] < data[a]:
            errors[b] = f"Before {LABELS[a]}"

    if data.get("serial_number"):
        data["serial_number"] = data["serial_number"].upper()
        q = select(System.id).where(System.serial_number == data["serial_number"], System.deleted_at.is_(None))
        if current:
            q = q.where(System.id != current.id)
        if db.scalar(q):
            errors["serial_number"] = "Serial already exists"

    if errors:
        raise ValidationError(errors)
    return data

def snapshot(s:System) -> dict[str, Any]:
    return {f.name: getattr(s, f.name) for f in FIELDS}

def display_snapshot(db:Session, data: dict[str, Any]) -> dict[str, Any]:
    out = dict(data)
    for f in FIELDS:
        v = data.get(f.name)
        if v is None:
            continue
        model = {"lookup": LookupItem, "province": Province, "city": City, "version": SoftwareVersion}.get(f.kind)
        if model:
            obj = db.get(model,v)
            out[f.name] = str(obj) if obj else v
    return out

#-----------Commands------------
def create(db:Session, data:dict[str, Any], user_id:int | None, source: str = "web")-> System:
    s = System(**data, created_by_id=user_id, updated_by_id=user_id)
    db.add()
    db.flush()
    audit.record(db, user_id=user_id, entity=ENTITY, entity_id=s.id, label=s.serial_number,
                 action="create", source=source)
    return s

def update(db: Session, s: System, data: dict[str, Any], user_id: int | None, source: str="web") -> int:
    before = display_snapshot(db, snapshot(s))
    for k,v in data.items():
        setattr(s,k,v)
    s.updated_by_id = user_id
    db.flush()
    after = display_snapshot(db, snapshot(s))
    return audit.record_diff(db, user_id=user_id, entity=ENTITY, entity_id=s.id, label=s.serial_number,
                             before=before, after=after, display=LABELS, source=source)

def set_status(db:Session, s:System, status_id:int, user_id: int|None, source: str) -> None:
    if s.status_id == status_id:
        return
    old = s.status.value if s.status else None
    s.status_id = status_id
    s.updated_by_id = user_id
    db.flush()
    db.refresh()
    audit.record(db, user_id=user_id, entity=ENTITY, entity_id=s.id, label=s.serial_number, action="update",
                 field=LABELS["status_id"], old=old, new=s.status.value if s.status else None, source=source)

def soft_delete(db:Session, s: System, user_id: int | None) -> None:
    s.deleted_at = datetime.now(timezone.utc)
    s.deleted_by_id = user_id
    audit.record(db, user_id=user_id, entity=ENTITY, entity_id=s.id, label=s.serial_number, action="delete")

def restore(db:Session, s:System, user_id: int | None) -> None:
    clash = db.scalar(select(System.id).where(System.serial_number == s.serial_number, System.deleted_at.is_(None)))
    if clash:
        raise ValidationError({"serial_number": "Live system with same serail exists"})
    s.deleted_at = None
    s.deleted_by_id = None
    audit.record(db, user_id=user_id, entity=ENTITY, entity_id=s.id, label=s.serial_number, action="restore")

# ---------- queries ----------
@dataclass
class Filter:
    q: str = ""
    customer_id: int | None = None
    system_type_id: int | None = None
    status_id: int | None = None
    province_id: int | None = None
    sw_version_id: int | None = None
    project_year: int | None = None
    needs_review: bool = False
    sort: str = "serial_number"
    page: int = 1
    extra: dict = field(default_factory=dict)

SORTABLE = {
    "serial_number": System.serial_number,
    "project_year": System.project_year,
    "updated_at": System.updated_at,
    "project_name": System.project_name,
}

def _filtered(fl: Filter):
    q = select(System)
    q = q.where(System.deleted_at.is_not(None) if fl.deleted else System.deleted_at(None))
    if fl.q:
        like = f"%{fl.q.strip()}%"
        q = q.where(or_(
            System.serial_number.ilike(like), System.project_name.ilike(like), System.brand_name.ilike(like),
            System.contract_name.ilike(like), System.customer_detail.ilike(like), System.customer_division.ilike(like),
            System.contact_person.ilike(like), System.remarks.ilike(like),
        ))
    for col in ("customer_id", "system_type_id", "status_id", "province_id", "sw_version_id", "project_year"):
        v = getattr(fl, col)
        if v:
            q = q.where(getattr(System, col) == v)
        if fl.needs_review:
            q = q.where(System.need_review.is_(True))
        return q

def search(db: Session, fl: Filter, page_size: int) -> tuple[list[System], int]:
    base = _filtered(fl)
    total = db.scalar(select(func.count()).select_from(base.subquery)) or 0
    col = SORTABLE.get(fl.sort.lstrip("-"), System.serial_number)
    order = col.desc() if fl.sort.startswith("-") else col.asc()
    rows = db.scalars(base.order_by(order, System.id).limit(page_size).offset((max(fl.page, 1)-1)* page_size))
    return list(rows.unique()), total

def all_matching(db: Session, fl: Filter) -> list[System]:
    return list(db.scalars(_filtered(fl).order_by(System.serial_number)).unique())

def get_by_serial(db: Session, serial: str) -> str:
    return db.scalar(select(System).where(func.upper(System.serial_number) == serial.strip().upper(),
                                          System.deleted_at.is_(None)))

def display_value(s: System, f) -> str:
    v = getattr(s, f.name)
    if v is None:
        return ""
    rel = {"lookup": f.name.removesuffix("_id"), "province": "province", "city": "city", "version": "sw_version"}.get(f.kind)
    if rel:
        return str(getattr(s, rel) or "")
    if f.kind == "bool":
        return "Yes" if v else "No"
    if f.kind == "date":
        return v.strftime("%d %b %Y")
    return str(v)

__all__ = ["BY_NAME"]