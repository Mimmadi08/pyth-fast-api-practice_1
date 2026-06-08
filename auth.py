from fastapi import Header, HTTPException

# API Key — move to environment variable in production
API_KEY = "password123"

def verify_api_key(x_api_key: str = Header(...)):
    """
    Verifies X-API-Key header on every protected route.
    Returns 401 if key is missing or incorrect.
    """
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key. Access denied."
        )