from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import ChatMemberUpdated


router = Router(name='user_events')


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_banned_bot(event: ChatMemberUpdated):
    print(f'user: {event.from_user.id} has blocked bot at {event.date}')


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unbanned_bot(event: ChatMemberUpdated):
    print(f'user: {event.from_user.id} decided to unblock bot at {event.date}')
