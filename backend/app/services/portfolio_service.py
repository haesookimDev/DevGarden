import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import PortfolioItem, PortfolioPostLink
from app.schemas.portfolio import PortfolioItemCreate, PortfolioItemUpdate


async def create_portfolio_item(db: AsyncSession, user_id: uuid.UUID, data: PortfolioItemCreate) -> PortfolioItem:
    item = PortfolioItem(user_id=user_id, **data.model_dump())
    db.add(item)
    await db.flush()
    return item


async def get_portfolio_items(
    db: AsyncSession,
    user_id: uuid.UUID,
    item_type: str | None = None,
) -> list[PortfolioItem]:
    query = select(PortfolioItem).where(PortfolioItem.user_id == user_id)
    if item_type:
        query = query.where(PortfolioItem.type == item_type)
    query = query.order_by(PortfolioItem.sort_order, PortfolioItem.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_portfolio_item_by_id(db: AsyncSession, item_id: uuid.UUID) -> PortfolioItem | None:
    result = await db.execute(select(PortfolioItem).where(PortfolioItem.id == item_id))
    return result.scalar_one_or_none()


async def update_portfolio_item(db: AsyncSession, item: PortfolioItem, data: PortfolioItemUpdate) -> PortfolioItem:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    await db.flush()
    return item


async def delete_portfolio_item(db: AsyncSession, item: PortfolioItem):
    await db.delete(item)
    await db.flush()


async def link_post_to_portfolio(db: AsyncSession, portfolio_item_id: uuid.UUID, post_id: uuid.UUID):
    link = PortfolioPostLink(portfolio_item_id=portfolio_item_id, post_id=post_id)
    db.add(link)
    await db.flush()
