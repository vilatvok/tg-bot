from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, any_state

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import reply
from database import queries
from states import AddUser
from utils.users import get_myself


router = Router()


@router.message(default_state, F.text == 'Fill in profile')
async def set_user(message: types.Message, state: FSMContext):
    await state.set_state(AddUser.gender)
    await message.answer(
        'Your gender',
        reply_markup=reply.gender_btns
    )


@router.message(AddUser.gender, F.text.in_(['Male', 'Female']))
async def set_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await state.set_state(AddUser.interested)
    await message.answer('Interested gender')


@router.message(AddUser.interested, F.text.in_(['Male', 'Female']))
async def set_interested(message: types.Message, state: FSMContext):
    await state.update_data(interested=message.text)
    await state.set_state(AddUser.age)
    await message.answer('Enter age', reply_markup=reply.cancel_btn)


@router.message(AddUser.age, F.text)
async def set_age(message: types.Message, state: FSMContext):
    if not str(message.text).isnumeric():
        await message.answer('Wrong format, age must contain only digits (10-100)')
        return
     
    if int(message.text) < 0 or int(message.text) > 100:
        await message.answer('Wrong value')
        return
    
    await state.update_data(age=int(message.text))
    await state.set_state(AddUser.username)
    await message.answer('Enter username', reply_markup=reply.cancel_btn)


@router.message(AddUser.username, F.text)
async def set_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await state.set_state(AddUser.description)
    await message.answer(
        'Enter your description: ', 
        reply_markup=reply.skip_btns
    )


@router.message(AddUser.description, F.text)
async def set_description(message: types.Message, state: FSMContext):
    if message.text == 'Skip':
        await message.answer('Choose image', reply_markup=reply.cancel_btn)
        await state.set_state(AddUser.image)
        return
    await state.update_data(description=message.text)
    await state.set_state(AddUser.image)
    await message.answer('Choose image', reply_markup=reply.cancel_btn)


@router.message(AddUser.image, F.photo)
async def set_image(message: types.Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await state.set_state(AddUser.city)
    await message.answer('Enter your city', reply_markup=reply.cancel_btn)


@router.message(AddUser.city, F.text)
async def set_city(
    message: types.Message, 
    state: FSMContext, 
    session: AsyncSession
):
    await state.update_data(city=message.text)
    data = await state.get_data()

    uuid = str(message.from_user.id)
    obj = await queries.get_user(session, uuid)
    if bool(obj):
        obj = await queries.update_user(session, uuid, data)
    else:
        obj = await queries.add_user(session, uuid, data)

    await get_myself(message, obj)
    await state.clear()


@router.message(any_state)
async def error_format(message: types.Message):
    await message.answer('Error validation, enter again')


@router.message(F.text == 'My profile')
async def get_my_profile(message: types.Message, session: AsyncSession):
    try:
        obj, rating = await queries.get_user(session, str(message.from_user.id))
    except TypeError:
        start = reply.generate_btns('Fill in profile')
        await message.answer(
            text='Your profile was deleted. Fill in it again',
            reply_markup=start
        )
    else:
        await get_myself(message, obj, rating)
