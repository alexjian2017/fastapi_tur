from datetime import datetime, timedelta
from hashlib import algorithms_available, algorithms_guaranteed
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .database import get_db
from .schemas import TokenData
from .models import User
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
# secret_key
# algorithms
# expiration time


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow()+timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.secret_key, settings.algorithm)


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.secret_key, [settings.algorithm])
        id = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="It's not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    user = db.query(User).filter(User.id == token.id).first()
    return user
