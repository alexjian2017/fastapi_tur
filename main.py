import uvicorn

from app import main

# Python API Development - Comprehensive Course for Beginners
# https://www.youtube.com/watch?v=0sOvCWFmrtA

if __name__ == "__main__":
    uvicorn.run(main.app, port=8000, host="0.0.0.0")
