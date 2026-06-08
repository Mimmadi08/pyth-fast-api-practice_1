from fastapi import Request
from fastapi.responses import JSONResponse

async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches ANY unhandled error in the entire app.
    Returns clean error message — never exposes
    internal code or stack traces to the user.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Something went wrong",
            "detail": "Please contact support"
        }
    )