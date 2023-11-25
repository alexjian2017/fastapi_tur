from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional, List


from ..models import Post, Vote
from ..schemas import PostCreate, PostResponse, PostOut
from ..database import engine, get_db
from ..utils import hash
from ..oauth2 import get_current_user

router = APIRouter(prefix='/posts', tags=['Posts'])


# @router.get("/", response_model=List[PostResponse])
@router.get("/", response_model=List[PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # posts = db.query(Post).all()
    # posts = db.query(Post).filter(Post.title.contains(
    #     search)).limit(limit).offset(skip).all()
    posts = db.query(Post, func.count(Vote.post_id).label("votes")).join(
        Vote, Post.id == Vote.post_id, isouter=True).group_by(Post.id).filter(
        Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_posts(post: PostCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # con.commit()
    new_post = Post(owner_id=current_user.id, **post.model_dump())
    # new_post = Post(title=post.title, content=post.content,
    #                        published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,))
    # post = cursor.fetchone()
    # post = db.query(Post).filter(Post.id == id).first()
    post = db.query(Post, func.count(Vote.post_id).label("votes")).join(
        Vote, Post.id == Vote.post_id, isouter=True).group_by(Post.id).filter(
        Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
    # delete_post = cursor.fetchone()
    # con.commit()
    post_query = db.query(Post).filter(Post.id == id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    if post_query.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")
    post_query.delete(synchronize_session=False)
    db.commit()


@router.put("/{id}", response_model=PostResponse)
def update_post(id: int, post: PostCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, id,))
    # updated_post = cursor.fetchone()
    # con.commit()
    post_query = db.query(Post).filter(Post.id == id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    if post_query.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()
