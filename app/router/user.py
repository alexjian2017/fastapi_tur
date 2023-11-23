from fastapi import FastAPI, HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session


from ..models import User, Post
from ..schemas import PostCreate, PostResponse, UserCreate, UserResponse
from ..database import engine, get_db
from ..utils import hash
router = APIRouter(prefix='/users', tags=['Users'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # hash the password
    user.password = hash(user.password)
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} was not found")

    return user
