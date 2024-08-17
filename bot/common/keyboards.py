from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

choose_role = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Репетитор')], [KeyboardButton(text='Учень')], [KeyboardButton(text='Батько/Мати')]],
    resize_keyboard=True, input_field_placeholder='Оберіть один із варіантів нижче')

choose_grade = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Я займаюсь без батьків')]],
    resize_keyboard=True, input_field_placeholder='Оберіть один із варіантів нижче')

skip_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Пропустити')]],
    resize_keyboard=True, input_field_placeholder='Оберіть один із варіантів нижче')
