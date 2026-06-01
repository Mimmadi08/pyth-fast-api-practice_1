from fastapi import FastAPI
from orders import router as orders_router    # ← ADD THIS
from exceptions import global_exception_handler

app = FastAPI()

# Global exception handler — catches ALL unhandled errors
# Must be registered before any routes          ← NEW
app.add_exception_handler(Exception, global_exception_handler)

# Day 1 routes
@app.get("/")
def hello():
    return {"message": "My first API is working!"}

@app.get("/greet/{name}")
def greet(name: str):
    return {"hello": name}

# Register orders routes              ← ADD THIS
app.include_router(orders_router)