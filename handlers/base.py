from aiogram import types, F, Router, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state

from sqlalchemy.ext.asyncio import AsyncSession
from handlers.profile import get_my_profile

from keyboards import reply
from database import queries
from keyboards.inline import main_btns
from states import ChangeUser
from utils.users import get_users_obj


router = Router()


@router.message(or_f(CommandStart(), F.text == 'Main'))
async def greetings(message: types.Message, session: AsyncSession):
    user = await queries.get_user(session, str(message.from_user.id))
    await reply.users_btns(message, user)


@router.message(Command('top'))
async def popular_users(message: types.Message, session: AsyncSession):
    user_id = str(message.from_user.id)
    users = await queries.get_popular_users(session, user_id)

    if users:
        await message.answer('🍭', reply_markup=reply.start_btns)
        for obj, rating in users:
            _rating_exist = await queries.get_rating(
                session,
                user_from_uuid=user_id,
                user_to_uuid=obj.uuid,
            )

            if not _rating_exist:
                reply_btn = main_btns(
                    btns={'Rate': 'rate'},
                    user_uuid=obj.uuid,
                )
            else:
                reply_btn = None

            await message.answer_photo(
                photo=obj.image,
                caption=f'{obj.username}, {obj.age}, {obj.city}\n'
                        f'Score: {rating}\n'
                        f'{obj.description if obj.description else ""}',
                reply_markup=reply_btn
            )
    else:
        await message.answer('Forbidden')


@router.message(Command('statistics'))
async def statistics(message: types.Message, session: AsyncSession):
    users = await queries.get_statistics(session)
    boys = f'{users["gender"][0][0]}: {users["gender"][0][1]}'
    girls = f'{users["gender"][1][0]}: {users["gender"][1][1]}'
    await message.answer(
        text=(
            f'Users registered: {users["all_users"]}\n'
            f'Active users: {users["active_users"]}\n'
            f'{boys}\n{girls}'
        ),
        reply_markup=reply.main_btn,
    )


@router.message(any_state, F.text == 'Cancel')
async def cancel_profile(
    message: types.Message,
    session: AsyncSession,
    state: FSMContext,
):
    current_state = await state.get_state()
    if not current_state:
        return

    if current_state.startswith('ChangeUser'):
        await state.set_state(ChangeUser.clause)
        await message.answer('Canceled', reply_markup=reply.edit_profile_btns)
        return

    await state.clear()
    user = await queries.get_user(session, str(message.from_user.id))
    if user:
        await message.answer('Canceled', reply_markup=reply.start_btns)
        return

    start = reply.generate_btns('Fill in profile')
    await message.answer(
        text='Fill in your profile',
        reply_markup=start,
    )


@router.message(F.text == 'Back')
async def back_page(
    message: types.Message,
    session: AsyncSession,
    state: FSMContext,
):
    current_state = await state.get_state()
    if not current_state:
        return

    await state.clear()
    await get_my_profile(message, session)


@router.message(F.text == 'Watch users')
async def get_users(message: types.Message, session: AsyncSession):
    await message.answer(
        text='🍭',
        reply_markup=reply.random_user_btns,
    )
    await get_users_obj(message, session, entry=True)


@router.message(F.text == '👎')
async def skip_user(message: types.Message, session: AsyncSession):
    await get_users_obj(message, session)


@router.message(F.text == '👍')
async def like_user(message: types.Message, bot: Bot, session: AsyncSession):
    obj = await get_users_obj(message, session)
    await bot.send_photo(
        obj.uuid,
        photo=obj.image,
        caption=f'{obj.username}, {obj.age}, {obj.city}\n'
                f'{obj.description if obj.description else ""}'
                f'{message.from_user.mention_html()} liked your profile.',
        parse_mode=ParseMode.HTML,
    )


@router.message(F.text == '😴')
async def leave_watching(message: types.Message, session: AsyncSession):
    await queries.update_user(
        session,
        uuid=str(message.from_user.id),
        data={'state': False},
    )
    await message.answer(
        text="""1. Fill profile
                2. My profile
                3. Watch users""",
        reply_markup=reply.start_btns
    )
