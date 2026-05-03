from functools import wraps

from fastapi import Depends, HTTPException

from backend.app.domain.entities import User
from backend.app.interface.auth.jwt_auth import get_current_user


def role_required(required_role: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if  required_role not in [current_user.role.value, "Admin"]:
                raise HTTPException(status_code=403, detail="Forbidden: Insufficient permissions")
            return func(*args, **kwargs)
        return wrapper
    return decorator
