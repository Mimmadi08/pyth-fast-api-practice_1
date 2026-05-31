from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
 return {"message": "This your first API call, and it is working!"}

@app.get("/greet/{name}")
def greet(name :str):
   return {"hello ":name}