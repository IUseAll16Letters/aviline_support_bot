__all__ = ("get_all_products", )

from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.models import Product, ProductProblem


async def get_all_products(db_session: AsyncSession) -> Sequence:
    """
    Get all current products (* that are marked as active *)
    :param db_session: AsyncSession as db_session from middleware DbSessionMiddleware
    """
    stmt = select(Product.name)
    result = await db_session.execute(stmt)

    return result.scalars().all()
