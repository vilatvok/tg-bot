from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class MenuCallback(CallbackData, prefix='menu'):
    level: int
    menu_name: str
    user_uuid: str


class AdminCallback(CallbackData, prefix='admin_menu'):
    level: int
    menu_name: str


def create_menu_btns(text, level, menu_name, user_uuid):
    btn = InlineKeyboardButton(
        text=text,
        callback_data=MenuCallback(
            level=level,
            menu_name=menu_name,
            user_uuid=user_uuid,
        ).pack(),
    )
    return btn


def main_btns(btns: dict, user_uuid):
    builder = InlineKeyboardBuilder()
    for text, btn in btns.items():
        if btn == 'rate':
            builder.add(create_menu_btns(
                text,
                level=0,
                menu_name=btn,
                user_uuid=user_uuid,
            ))
        else:
            builder.add(create_menu_btns(
                text,
                level=1,
                menu_name=btn,
                user_uuid=user_uuid,
            ))
    return builder.as_markup()


def report_btns(btns: dict, user_uuid):
    builder = InlineKeyboardBuilder()
    for text, btn in btns.items():
        if btn == 'back':
            builder.add(create_menu_btns(
                text,
                level=0,
                menu_name=btn,
                user_uuid=user_uuid,
            ))
        else:
            builder.add(create_menu_btns(
                text,
                level=1,
                menu_name=btn,
                user_uuid=user_uuid,
            ))
    return builder.as_markup()


def admin_btns(btns: dict):
    builder = InlineKeyboardBuilder()
    for text, btn in btns.items():
        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=AdminCallback(
                    level=1,
                    menu_name=btn,
                ).pack()
            )
        )
    return builder.as_markup()


def back_btn():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='Back',
            callback_data=AdminCallback(
                level=0,
                menu_name='back',
            ).pack(),
        )
    )
    return builder.as_markup()


def delete_btn(user_uuid):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='Delete',
            callback_data=f'delete_{user_uuid}',
        )
    )
    return builder.as_markup()
