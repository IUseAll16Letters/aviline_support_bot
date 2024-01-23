import pytest

from sqlalchemy import select

from tgbot.crud import TicketRelatedQueries
from tgbot.models import Ticket


test_data = [
    [1, 'test_question', 123, False],
    [2, 'second_question', 444, False]
]


@pytest.mark.asyncio
@pytest.mark.parametrize("ticket_id, question, user_id, is_solved", test_data)
async def test_create_ticket(session, ticket_id, question, user_id, is_solved):
    print(session)
    res = await TicketRelatedQueries(session).create_ticket(
        question=question,
        user_telegram_id=user_id,
    )
    assert res == (1, )
    stmt = select(Ticket)
    ticket: Ticket = (await session.execute(stmt)).first()[0]
    assert ticket.id == ticket_id \
           and ticket.question == question \
           and ticket.customer == user_id \
           and ticket.is_solved == is_solved
