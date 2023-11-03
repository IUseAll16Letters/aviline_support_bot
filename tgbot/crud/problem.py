__all__ = ("get_product_problems", "get_problem_solution")

from typing import Any

from sqlalchemy import select, Sequence, Row
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.models import Product, ProductProblem


async def get_product_problems(db_session: AsyncSession, product: str) -> Sequence[Any]:
    """
    Get all current product problems from database by product name as str
    :param db_session: AsyncSession as db_session from middleware DbSessionMiddleware
    :param product: str prod name
    """
    stmt = select(ProductProblem.title).join_from(ProductProblem, Product).filter(
        Product.name == product,
        Product.is_active == 1,
    )
    result = await db_session.execute(stmt)

    return result.scalars().all()


async def get_problem_solution(db_session: AsyncSession, product: str, problem_order: int) -> Row:
    """
    Get product problem and its solution by name as str and order as int
    :param db_session: AsyncSession as db_session from middleware DbSessionMiddleware
    :param product: str prod name
    :param problem_order: int problem order starting from 0
    """
    stmt = select(ProductProblem.title, ProductProblem.solution, ProductProblem.attachment)\
        .join_from(ProductProblem, Product)\
        .filter(
        Product.name == product,
        Product.is_active == 1,
    )
    result = await db_session.execute(stmt)

    return result.fetchall()[problem_order]
