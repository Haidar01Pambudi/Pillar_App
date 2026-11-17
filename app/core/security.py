import hmac
import secrets

import bcrypt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.permissions import has_permission
from app.db import get_db
from app.modules.auth.models import User

def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode()[:72], bcrypt.gensalt(rounds=12)).decode()

def verify_password(raw: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(raw.encode()[:72], hashed.encode())
    except ValueError:
        return False

class NotAuthenticated(Exception):
    pass

class Forbidden(Exception):
    def __init__(self, prem: str):
        self.prem = prem

def current_user(request:Request, db:Session=Depends(get_db))->User:
    uid = request.session.get("uid")
    if not uid:
        raise NotAuthenticated()
    user = db.get(User, uid)
    if not user or not user.is_active:
        request.session.clear()
        raise NotAuthenticated()
    request.state.user = user
    return user

def require(perm: str):
    def dep(user: User = Depends(current_user)) -> User:
        if not has_permission(user.role, perm):
            raise Forbidden(perm)
        return user
    return dep

def csrf_token(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token

async def csrf_protect(request: Request) -> None:
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    expected = request.session.get("csrf")
    sent = request.headers.get("x-csrf-token")
    if not sent:
        form = await request.form()
        sent = form.get("csrf_token")
    if not expected or not sent or not hmac.compare_digest(str(sent), expected):
        raise HTTPException(status_code=403, detail="CSRF token invalid. Reload page.")
    