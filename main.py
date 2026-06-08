from fastapi import FastAPI
from orders import router as orders_router
from exceptions import global_exception_handler

app = FastAPI(
    title="OMS Order Management API",
    description="REST API for managing OMS Pre-Order Headers",
    version="1.0.0"
)

# Global exception handler — catches all unhandled errors
app.add_exception_handler(Exception, global_exception_handler)

# Day 1 routes
@app.get("/")
def hello():
    return {"message": "OMS Order API is running!"}

@app.get("/greet/{name}")
def greet(name: str):
    return {"hello": name}

# Register all order routes
app.include_router(orders_router)