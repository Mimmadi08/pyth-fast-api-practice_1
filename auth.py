from fastapi import Header, HTTPException

# Your API Key
# In production this would come from
# environment variables — never hardcode in real apps!
API_KEY = "password123"

def verify_api_key(x_api_key: str = Header(...)):
    """
    Checks X-API-Key header on every
    protected request.
    """
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key. Access denied."
        )