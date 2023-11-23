import time
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, Depends
from numpy import deprecate
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
import uvicorn

import models
from schemas import PostCreate, PostResponse, UserCreate, UserResponse
from database import engine, get_db
from utils import hash

# uvicorn main:app --host 127.0.0.1 --port 8000 --reload
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while 1:
    try:
        con = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
                               password='12345678a', cursor_factory=RealDictCursor)
        cursor = con.cursor()
        print('Connecting to Database successfully')
        break
    except Exception as e:
        print(f'Connecting to Database failed {e}')
        time.sleep(5)


@app.get("/")
def root():
    return {"msg": "hello world"}


@app.get("/posts", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_posts(post: PostCreate, db: Session = Depends(get_db)):
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # con.commit()
    new_post = models.Post(**post.model_dump())
    # new_post = models.Post(title=post.title, content=post.content,
    #                        published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/{id}", response_model=PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
    # delete_post = cursor.fetchone()
    # con.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    post_query.delete(synchronize_session=False)
    db.commit()


@app.put("/posts/{id}", response_model=PostResponse)
def update_post(id: int, post: PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, id,))
    # updated_post = cursor.fetchone()
    # con.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # hash the password
    user.password = hash(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} was not found")

    return user


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="127.0.0.1")
