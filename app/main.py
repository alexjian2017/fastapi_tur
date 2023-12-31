from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .router import post, user, auth, vote
from .models import Base
from .database import engine

# uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"msg": "hello world"}
