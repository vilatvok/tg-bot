from aiogram import types, F, Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import reply
from database import queries
from keyboards.inline import MenuCallback
from states import ChangeUser
from utils.users import get_myself, get_content


router = Router()


@router.message(default_state, F.text == 'Edit profile')
async def edit_profile(message: types.Message, state: FSMContext):
    await state.set_state(ChangeUser.clause)
    await message.answer(
        text="""1. Change username
                2. Change image
                3. Change description""",
        reply_markup=reply.edit_profile_btns,
    )


@router.message(ChangeUser.clause)
async def change_user(message: types.Message, state: FSMContext):
    await state.update_data(clause=message.text)
    data = (await state.get_data())
    match data['clause']:
        case '1':
            await state.set_state(ChangeUser.username)
            await message.answer(
                text='Enter new username',
                reply_markup=reply.cancel_btn,
            )
        case '2':
            await state.set_state(ChangeUser.image)
            await message.answer(
                text='Choose new image',
                reply_markup=reply.cancel_btn,
            )
        case '3':
            await state.set_state(ChangeUser.description)
            await message.answer(
                text='Enter new description',
                reply_markup=reply.cancel_btn,
            )
        case _:
            await message.answer('Wrong clause, try again')


@router.message(
    or_f(
        ChangeUser.username,
        ChangeUser.description,
        ChangeUser.image,
    ),
)
async def change_user_field(
    message: types.Message,
    session: AsyncSession,
    state: FSMContext,
):
    current_state = await state.get_state()
    try:
        match current_state:
            case ChangeUser.username:
                await state.update_data(username=message.text)
            case ChangeUser.description:
                await state.update_data(description=message.text)
            case ChangeUser.image:
                await state.update_data(image=message.photo[-1].file_id)
    except TypeError:
        await message.answer('Wrong format, try again')
        return

    data = await state.get_data()
    obj = await queries.update_user(session, str(message.from_user.id), data)

    await get_myself(message, obj)
    await state.clear()


@router.callback_query(MenuCallback.filter())
async def rate_user(
    callback: types.CallbackQuery,
    callback_data: MenuCallback,
    session: AsyncSession,
):
    if callback_data.menu_name == 'rate':
        await queries.set_rating(
            session,
            user_from_uuid=str(callback.from_user.id),
            user_to_uuid=callback_data.user_uuid,
        )
        await callback.message.edit_reply_markup()
        await callback.answer('Rated')

    elif callback_data.menu_name not in ['back', 'report']:
        await queries.send_report(
            session,
            user_from_uuid=str(callback.from_user.id),
            user_to_uuid=callback_data.user_uuid,
            reason=callback_data.menu_name,
        )
        await callback.message.edit_reply_markup()
        await callback.answer('Reported')

    else:
        reply = await get_content(
            session=session,
            level=callback_data.level,
            user_from_id=str(callback.from_user.id),
            user_to_id=callback_data.user_uuid,
        )
        await callback.message.edit_reply_markup(reply_markup=reply)
