__all__ = ("create_visitor", )

from datetime import datetime
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.models import Visitor


async def create_visitor(
        db_session: AsyncSession,
        user_id: int,
        username: str,
        firstname: str = None,
        lastname: str = None,
        created_at: datetime = datetime.now(),
):
    stmt = insert(Visitor)\
        .values(username=username, user_id=user_id, firstname=firstname, lastname=lastname, created_at=created_at)
    res = await db_session.execute(stmt)
    print(res)
