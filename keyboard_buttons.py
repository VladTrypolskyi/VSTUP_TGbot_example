from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from db_map import DatabaseMapper


class Keyboard():
    ''' Keyboard for reply markups '''

    button_add = KeyboardButton('Додати оцiнки ЗНО')
    button_my = KeyboardButton('Мої бали')
    button_where = KeyboardButton('Куди я можу вступити?')

    home = ReplyKeyboardMarkup(resize_keyboard=True)
    home.add(button_add, button_my)
    home.add(button_where)


class Buttons():
    ''' Buttons for Inline keyboard '''

    znos = DatabaseMapper().all_znos()

    select_zno = InlineKeyboardMarkup(row_width=2)
    for zno in znos:
        # Using st bcs of 64byte data limit
        select_zno.insert(InlineKeyboardButton(
            text=zno, callback_data=f'st{zno}'))

    areas = DatabaseMapper().all_areas()

    select_area = InlineKeyboardMarkup(row_width=2)
    for area in areas:
        # Split bcs of 64byte limit
        select_area.insert(InlineKeyboardButton(
            text=area.name, callback_data=area.id))

    def gen_specs(area):
        ''' Generate  inly keyboard for area'''

        specs = DatabaseMapper().specs(area)

        select_spec = InlineKeyboardMarkup(row_width=2)
        print(specs)
        for spec in specs:
            # Using bcs of 64byte data limit
            select_spec.insert(InlineKeyboardButton(
                text=spec.name, callback_data=spec.id))
        select_spec.add(InlineKeyboardButton(
            text='Усi спецiальностi', callback_data='all'))
        select_spec.add(InlineKeyboardButton(
            text='Назад', callback_data='back'))

        return (select_spec)
