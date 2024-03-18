from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def generate_btns(*btns):
    builder = ReplyKeyboardBuilder()
    for btn in btns:
        builder.add(KeyboardButton(text=btn))
    return builder.as_markup(resize_keyboard=True)


start_btns = generate_btns('Fill in profile', 'My profile', 'Watch users')


async def users_btns(message: Message, user):
    if user:
        start = start_btns
        await message.answer(
            text='1. Fill in profile\n'
                '2. My profile\n'
                '3. Watch users',
            reply_markup=start
        )
    else:
        start = generate_btns('Fill in profile')
        await message.answer(
            text='Fill in your profile',
            reply_markup=start
        )


gender_btns = generate_btns('Male', 'Female', 'Cancel')
skip_btns = generate_btns('Skip', 'Cancel')
random_user_btns = generate_btns('👍', '👎', '😴')
edit_btns = generate_btns('Edit profile', 'Main')
edit_profile_btns = generate_btns('1', '2', '3', 'Back')
main_btn = generate_btns('Main')
cancel_btn = generate_btns('Cancel')