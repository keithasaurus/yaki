import uvicorn

from src.applications import application

if __name__ == '__main__':
    uvicorn.run(application(), host='0.0.0.0', port=8000)