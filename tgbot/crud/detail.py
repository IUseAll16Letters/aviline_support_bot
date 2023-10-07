__all__ = ("get_product_detail", )

from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.models import Product, ProductDetail


async def get_product_detail(db_session: AsyncSession, product_name: str) -> Sequence:
    stmt = select(Product.name, ProductDetail.title, ProductDetail.description, ProductDetail.attachment)\
        .join_from(ProductDetail, Product, full=True)\
        .where(Product.name == product_name)
    res = await db_session.execute(stmt)
    return res.fetchall()
