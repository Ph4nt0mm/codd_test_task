import uvicorn

from app.handlers.metro import app

if __name__ == '__main__':
    uvicorn.run(app=app, port=8002)
