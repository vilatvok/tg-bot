from aiogram.types import Message

from keyboards.inline import main_btns, report_btns
from keyboards.reply import edit_btns
from database.queries import get_users, update_user, get_rating


async def get_myself(message: Message, obj, rating=0):
    await message.answer_photo(
        photo=obj.image,
        caption=f'{obj.username}, {obj.age}, {obj.city}\n'
                f'Score: {rating}\n'
                f'{obj.description if obj.description else ""}',
        reply_markup=edit_btns,
    )


async def get_user_obj(message: Message, session, obj, rating=0):
    reply_btn = await get_content(
        session,
        level=0,
        user_from_id=str(message.from_user.id),
        user_to_id=obj.uuid,
    )
    await message.answer_photo(
        photo=obj.image,
        caption=f'{obj.username}, {obj.age}, {obj.city}\n'
                f'Score: {rating}\n'
                f'{obj.description if obj.description else ""}',
        reply_markup=reply_btn,
    )


async def get_users_obj(message: Message, session, entry=False):
    try:
        obj, rating = await get_users(session, str(message.from_user.id))
        if entry:
            await update_user(
                session,
                uuid=str(message.from_user.id),
                data={'state': True},
            )
        await get_user_obj(message, session, obj, rating)
    except (AttributeError, TypeError):
        await message.answer('No users found')
    else:
        return obj


async def get_content(session, level, user_from_id, user_to_id):
    _rating_exist = await get_rating(session, user_from_id, user_to_id)
    if level == 0:
        if _rating_exist:
            return main_btns(
                btns={'Report': 'report'},
                user_uuid=user_to_id,
            )
        else:
            return main_btns(
                btns={'Rate': 'rate', 'Report': 'report'},
                user_uuid=user_to_id,
            )
    elif level == 1:
        return report_btns(
            btns={
                'Back': 'back',
                'Spam': 'spam',
                'Bad image': 'image',
            },
            user_uuid=user_to_id,
        )
