from aiogram.dispatcher.filters.state import State, StatesGroup


# Additional file for states
# In future states can be added

class Grades(StatesGroup):
    ''' States of bot '''
    grade = State()
    choose_area = State()
    choose_spec = State()
