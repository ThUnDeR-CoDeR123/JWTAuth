from fastapi import FastAPI
from app.routes.auth import router
from app.database import  engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)

@app.get('/')
def home():
    return {"hello": "world"}
