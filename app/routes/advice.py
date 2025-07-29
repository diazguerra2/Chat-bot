from fastapi import APIRouter, Depends
from app.middleware.auth import verify_token


router = APIRouter()


@router.get("/")
async def get_advice(current_user: dict = Depends(verify_token)):
    """Get general advice endpoint (placeholder)"""
    return {
        "message": "Advice endpoint - to be implemented based on requirements",
        "userId": current_user['userId']
    }
