from aiogram import F, Router, types
from aiogram.filters import Command, CommandObject

from sqlalchemy.ext.asyncio import AsyncSession
from database.queries import delete_user, get_user

from filters import IsAdmin
from keyboards.inline import AdminCallback
from utils.admin import admin_menu, admin_get_user


router = Router()
router.message.filter(IsAdmin())


@router.message(Command('admin'))
async def admin_get_users(message: types.Message, session: AsyncSession):
    text, btns = await admin_menu(level=0, session=session)
    await message.answer(
        text=text,
        reply_markup=btns
    )


@router.callback_query(AdminCallback.filter())
async def admin_callback(
    callback: types.CallbackQuery,
    callback_data: AdminCallback,
    session: AsyncSession,
):
    text, btns = await admin_menu(
        level=callback_data.level,
        session=session,
        menu_name=callback_data.menu_name,
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=btns,
    )
    await callback.answer()


@router.message(Command('search'))
async def search_user(
    message: types.Message,
    command: CommandObject,
    session: AsyncSession,
):
    if not command.args:
        await message.answer('Error, search must contain uuid')
        return
    try:
        user, rating = await get_user(session, command.args)
    except TypeError:
        await message.answer('User not found')
    else:
        await admin_get_user(message, user, rating)


@router.callback_query(F.data.startswith('delete_'))
async def rate_user(
    callback: types.CallbackQuery,
    session: AsyncSession,
):
    user = callback.data.split('_')[-1]
    await delete_user(session, user)
    await callback.answer('Deleted', show_alert=True)
    await callback.message.delete()
