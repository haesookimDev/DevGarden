import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.portfolio import PortfolioItemCreate, PortfolioItemResponse, PortfolioItemUpdate
from app.services import portfolio_service

router = APIRouter()


@router.get("", response_model=list[PortfolioItemResponse])
async def list_portfolio_items(
    type: str | None = None,
    user_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List portfolio items for a user."""
    target_user_id = user_id or current_user.id
    items = await portfolio_service.get_portfolio_items(db, target_user_id, item_type=type)
    return [PortfolioItemResponse.model_validate(item) for item in items]


@router.post("", response_model=PortfolioItemResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio_item(
    data: PortfolioItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new portfolio item."""
    item = await portfolio_service.create_portfolio_item(db, current_user.id, data)
    return PortfolioItemResponse.model_validate(item)


@router.put("/{item_id}", response_model=PortfolioItemResponse)
async def update_portfolio_item(
    item_id: uuid.UUID,
    data: PortfolioItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a portfolio item."""
    item = await portfolio_service.get_portfolio_item_by_id(db, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")
    item = await portfolio_service.update_portfolio_item(db, item, data)
    return PortfolioItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a portfolio item."""
    item = await portfolio_service.get_portfolio_item_by_id(db, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")
    await portfolio_service.delete_portfolio_item(db, item)
