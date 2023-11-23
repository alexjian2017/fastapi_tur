import uvicorn

from app import main

if __name__ == "__main__":
    uvicorn.run(main.app, port=8000, host="127.0.0.1")
