from functools import wraps

from app.domain.entities import User
from app.interface.auth.jwt_auth import get_current_user
from fastapi import Depends, HTTPException


def role_required(*required_roles: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            user_role = current_user.role.value
            allowed = user_role == "Admin" or user_role in required_roles
            if not allowed:
                raise HTTPException(status_code=403, detail="Forbidden: Insufficient permissions")
            return func(*args, **kwargs)
        return wrapper
    return decorator
