from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from db_map import DatabaseMapper
from bot_states import Grades
from keyboard_buttons import Buttons, Keyboard
from config import TOKEN

db = DatabaseMapper()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

''' For menu '''


@dp.message_handler(commands=['help', 'start'], state='*')
async def hello(message: types.Message):
    await message.answer('''
        Привiт! Цей бот допоможе вам дiзнатись куди ви можете поступити!''',
                         reply_markup=Keyboard.home)
    db.create_user(message.from_user.id)


@dp.message_handler(Text(equals='Назад', ignore_case=True), state='*')
async def get_grades(message: types.Message, state: FSMContext):
    await message.answer('Повертаємось назад...',
                         reply_markup=Keyboard.home)
    await state.finish()


''' Choose method '''


@dp.message_handler(Text(equals='Додати оцiнки ЗНО', ignore_case=True), state='*')
async def get_grades(message: types.Message):
    msg = await message.answer('Оберiть предмет:',
                               reply_markup=Buttons.select_zno)


@dp.message_handler(Text(equals='Мої бали', ignore_case=True), state='*')
async def get_grades(message: types.Message):
    grades = '\n'.join(db.get_grades(message.from_user.id))
    if not grades:
        await message.answer("У вас немає оцiнок.")
    else:
        await message.answer('\n'.join(db.get_grades(message.from_user.id)))


''' Working with grades '''


@dp.callback_query_handler(Text(startswith='st'), state='*')
async def set_zno_grade(callback_query: types.CallbackQuery, state: FSMContext):
    subject = callback_query.data.split('st')[1]

    '''Change state for adding grade'''
    async with state.proxy() as data:
        data['subject'] = subject

    await Grades.grade.set()
    await callback_query.answer()
    await callback_query.message.answer(f'Введiть балл з: {subject}\nДля видалення введiть 0',
                                        reply_markup=types.ReplyKeyboardMarkup(
                                            resize_keyboard=True).add(types.KeyboardButton('Назад')))


''' setting grade and finish state '''


@dp.message_handler(state=Grades.grade)
async def math(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # validation for grade
        try:
            data['grade'] = float(message.text)

            if (data['grade'] >= 100 and data['grade'] <= 200) or data['grade'] == 0:
                await message.answer(db.set_grade(
                    message.from_user.id, {'name': data['subject'], 'grade': data['grade']}),
                    reply_markup=Keyboard.home)
                await state.finish()

            else:
                raise ValueError

        except ValueError:
            await message.answer('Невiрне значення')


''' choose area '''


@dp.message_handler(Text(equals='Куди я можу вступити?', ignore_case=True), state='*')
async def get_grades(message: types.Message):
    await message.answer("Оберiть галузь знань:",
                         reply_markup=Buttons.select_area)
    await Grades.choose_area.set()


@dp.callback_query_handler(state=Grades.choose_area)
async def choose_area(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['area'] = callback_query.data
    await callback_query.message.edit_text('Оберiть спецiальнiсть')
    await callback_query.message.edit_reply_markup(Buttons.gen_specs(callback_query.data))
    # await callback_query.message.edit_reply_markup(Buttons.gen_specs(callback_query.data))
    await Grades.choose_spec.set()
    await callback_query.answer()


@dp.callback_query_handler(state=Grades.choose_spec)
async def choose_spec(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'all':
        async with state.proxy() as data:
            abilities = db.grades_for_spec(
                tg_id=callback_query.from_user.id, area=data['area'])
        if abilities['budget'] or abilities['contract']:
            nl = '\n'
            message = f'''*Ви можете поступити на бюджет:*\n{nl.join(
                abilities['budget'])}\n\n *На контракт:*\n{nl.join(abilities['contract'])}'''
            await callback_query.message.answer(message, parse_mode=types.ParseMode.MARKDOWN)
        else:
            await callback_query.message.answer('Нажаль ви не можете поступити в цiй галузi.')
    elif callback_query.data == 'back':
        await callback_query.message.edit_text('Оберiть галузь знань')
        await callback_query.message.edit_reply_markup(Buttons.select_area)
        await Grades.choose_area.set()
    else:
        await callback_query.message.answer(db.grades_for_spec(
            tg_id=callback_query.from_user.id, spec=callback_query.data))
    await callback_query.answer()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
