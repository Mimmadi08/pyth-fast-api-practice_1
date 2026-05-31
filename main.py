from fastapi import FastAPI
from orders import router as orders_router    # ← ADD THIS

app = FastAPI()

# Day 1 routes
@app.get("/")
def hello():
    return {"message": "My first API is working!"}

@app.get("/greet/{name}")
def greet(name: str):
    return {"hello": name}

# Register orders routes              ← ADD THIS
app.include_router(orders_router)