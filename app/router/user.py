from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session


from ..models import User
from ..schemas import UserCreate, UserResponse
from ..database import engine, get_db
from ..utils import hash
router = APIRouter(prefix='/users', tags=['Users'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # check user's email unique
    exist_user = db.query(User).filter(User.email == user.email).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with email: {user.email} was already exist")
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
