"""
User Management API Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_superuser, get_db
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter()


@router.get("", response_model=List[UserRead], summary="List All Registered Users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_superuser)
) -> List[UserRead]:
    """Lists registered users (Administrator privilege required)."""
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserRead, summary="Get User Details by ID")
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_superuser)
) -> UserRead:
    """Retrieves user account details by user ID."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found."
        )

    return user
