from fastapi import FastAPI

# This creates your API application
app = FastAPI()

# @app.get("/") means:
# when someone visits the "/" URL, run this function
@app.get("/")
def hello():
    return {"message": "My first API is working!"}

# A route with a variable in the URL
# whatever name you type in the URL comes in as 'name'
@app.get("/greet/{name}")
def greet(name: str):
    return {"hello": name}