import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.domain.entities import User
from backend.app.domain.enums import role

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, "your_secret_key", algorithms=["HS256"])
        user = User(
            id=payload["id"],
            username=payload["username"],
            password_hash=payload["password_hash"],
            created_at=payload["created_at"],
            last_login=payload["last_login"],
            role=role.Role(payload["role"])
        )
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
