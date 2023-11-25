from fastapi import FastAPI
from numpy import deprecate

import uvicorn
from .utils import hash
from .router import post, user, auth, vote
from .models import Base
from .database import engine, get_db

# uvicorn main:app --host 127.0.0.1 --port 8000 --reload
Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"msg": "hello world"}


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="127.0.0.1", reload=True)
