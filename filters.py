from aiogram.types import Message
from aiogram.filters import Filter

from config import ADMIN_ID


class IsAdmin(Filter):
    async def __call__(self, message: Message):
        return str(message.from_user.id) in [ADMIN_ID]
