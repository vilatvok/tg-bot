from aiogram import types

from database.queries import get_all_users, get_reports
from keyboards.inline import admin_btns, back_btn, delete_btn


def admin_get_main():
    text = 'Select one option'
    btns = admin_btns({
        'Users': 'users',
        'Reports': 'reports',
    })
    return text, btns


async def admin_get_user(message: types.Message, user, rating):
    reply_btn = delete_btn(user.uuid)
    await message.answer_photo(
        photo=user.image,
        caption=f'Username: {user.username}\n'
                f'Age: {user.age}\n'
                f'City: {user.city}\n'
                f'Gender: {user.gender}\n'
                f'Interested: {user.interested}\n'
                f'Score: {rating}\n'
                f'Description: {user.description if user.description else ""}',
        reply_markup=reply_btn,
    )


async def admin_get_users(session):
    users = await get_all_users(session)
    text = ''
    for user in users:
        text += f'{user.username} - {user.age} - {user.uuid}\n'
    btn = back_btn()
    return text, btn


async def admin_get_reports(session):
    reports = await get_reports(session)
    text = ''
    for report in reports:
        text += (
            f'{report[0]} report to {report[1]}:'
            f'{report[2]} for {report[3]}\n'
        )
    if not len(text):
        text = 'No reports'
    btn = back_btn()
    return text, btn


async def admin_menu(level, session, menu_name=None):
    if level == 0:
        return admin_get_main()
    elif level == 1:
        if menu_name == 'users':
            return await admin_get_users(session)
        else:
            return await admin_get_reports(session)
