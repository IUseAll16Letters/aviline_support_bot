__all__ = ("ProductRelatedQueries",)

from sqlalchemy import select, Sequence, func, column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from tgbot.models import Product


class ProductRelatedQueries:
    def __init__(self, db_session: AsyncSession):
        """:param db_session: AsyncSession as db_session from middleware DbSessionMiddleware"""
        self.db_session = db_session

    async def get_all_products(self) -> Sequence:
        """Get all current products (* that are marked as active and don't have parent*)"""
        stmt = select(Product.name).where(
            column("is_subproduct_of_id").is_(None) & column("is_active").is_(True),
        )
        res = await self.db_session.execute(stmt)

        return res.scalars().all()

    async def get_product_detail(self, product_name: str) -> Sequence:
        """Get details from selected product by prod name taken from query"""
        stmt = select(Product.description, Product.attachment) \
            .where(Product.name == product_name)
        res = await self.db_session.execute(stmt)
        return res.first()

    async def count_sub_products(self, prod_name: str) -> int:
        """Count amount of sub products for selected product by prod name taken from query"""
        prod_alias = aliased(Product)
        stmt = select(func.count(prod_alias.name)) \
            .join(Product.subproduct.of_type(prod_alias)) \
            .filter(
                Product.name == prod_name,
                prod_alias.is_active == 1,
                prod_alias.is_subproduct_of_id == Product.id,
        )
        res = await self.db_session.execute(stmt)
        data = res.first()
        return data[0]

    async def get_sub_products(self, prod_name: str) -> Sequence:
        """Get all sub products for selected product by prod name taken from query"""
        prod_alias = aliased(Product)
        stmt = select(prod_alias.name) \
            .join(Product.subproduct.of_type(prod_alias)) \
            .filter(
                Product.name == prod_name,
                prod_alias.is_active == 1,
                prod_alias.is_subproduct_of_id == Product.id,
        )
        res = await self.db_session.execute(stmt)
        return res.scalars().all()
