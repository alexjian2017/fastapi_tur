import time

from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, Depends
from numpy import deprecate
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
import uvicorn

from .utils import hash
from .router import post, user
from . import models
from .database import engine, get_db

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

app.include_router(post.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {"msg": "hello world"}


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="127.0.0.1")
