import os
import time
import datetime
import telebot
from telebot import types
from environs import Env
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saloon.settings')
application = get_wsgi_application()

from sql_functions import (
    sql_get_user_data,
    sql_register_new_user,
    sql_put_user_phone,
    sql_add_feedback,
    get_masters_name_from_base,
    get_services_from_base,
    get_free_time_for_master,
    get_free_time_for_procedure,
    get_past_appointment,
    registration_new_appointment,
    restoring_user_date_for_sql_query,
)

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


env = Env()
env.read_env(override=True)
bot = telebot.TeleBot(env.str("TELEGRAM_CLIENT_BOT_API_TOKEN"))


def print_booking_text(user_data, not_confirmed=True):

    if not_confirmed:
        dialogue_text = ' ---- Бронирование Записи ----' + '\n\n'
    else:
        dialogue_text = 'Поздравляем с успешной записью!' + '\n'
        dialogue_text += '===============================' + '\n\n'

    if user_data["procedure"]:
        dialogue_text += f'Сервис: {user_data["procedure"]["title"]}' + '\n'
    if user_data["master"]:
        dialogue_text += f'Мастер: {user_data["master"]["name"]}' + '\n'
        # dialogue_text += 'Услуга: {}' + '\n'
    if user_data["date"]:
        dialogue_text += f'Дата: {user_data["date"]}' + '\n'
    if user_data["time"]:
        dialogue_text += f'Время: {user_data["time"]}' + '\n'

    dialogue_text += '\n'

    return dialogue_text


# Приветствие и кнопка START
@bot.message_handler(commands=['start'])
def start_menu(message):
    if 'users' not in bot.__dict__.keys():
        bot.__dict__.update({'users': {}})

    bot.__dict__['users'].update({
        message.chat.id: {
            'user_id': sql_get_user_data(message.chat.id),
            'first_time': True,
            'office': False,
            'master': False,
            'procedure': False,
            'date': False,
            'time': False,
            'phone': False,
            'last_message_id': False
            }})

    user_data = bot.__dict__['users'][message.chat.id]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text='📞 Позвонить нам'))
    bot.send_message(message.chat.id, 'Добро пожаловать в BeautyCity!!!', reply_markup=markup)
    bot.register_next_step_handler(message, call_us)

    user_in_db = sql_get_user_data(message.chat.id)
    if user_in_db:
        user_data['first_time'] = False
        user_data['phone'] = user_in_db['phone']

    dialogue_text = 'Выберите пункт меню:'
    markup_inline = types.InlineKeyboardMarkup(row_width=1)
    about_button = types.InlineKeyboardButton("О Нас", callback_data='about')
    choose_master_button = types.InlineKeyboardButton("Выбор мастера", callback_data='choose_master')
    choose_procedure_button = types.InlineKeyboardButton("Выбор процедуры", callback_data='choose_procedure')
    markup_inline.add(about_button, choose_master_button, choose_procedure_button)
    if user_data['user_id'] and get_past_appointment(user_data['user_id']['id']):
        markup_inline.add(types.InlineKeyboardButton("Оставить отзыв", callback_data='send_feedback'))
    bot.send_message(message.chat.id, dialogue_text, reply_markup=markup_inline)


def main_menu(message):
    user_data = bot.__dict__['users'][message.chat.id]
    dialogue_text = 'Выберите пункт меню:'
    markup = types.InlineKeyboardMarkup(row_width=1)
    about_button = types.InlineKeyboardButton("О Нас", callback_data='about')
    choose_master_button = types.InlineKeyboardButton("Выбор мастера", callback_data='choose_master')
    choose_procedure_button = types.InlineKeyboardButton("Выбор процедуры", callback_data='choose_procedure')

    markup.add(about_button, choose_master_button, choose_procedure_button)
    if user_data['user_id'] and get_past_appointment(user_data['user_id']['id']):
        markup.add(types.InlineKeyboardButton("Оставить отзыв", callback_data='send_feedback'))
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    if 'users' not in bot.__dict__.keys():      # Если сервер перезапускался, то клиент вернётся на стартовую страницу
        bot.__dict__.update({'users': {}})
        bot.delete_message(call.message.chat.id, call.message.id)
        start_menu(call.message)
        call.data = ''

    user_data = bot.__dict__['users'][call.message.chat.id]
    args = call.data.split('#')
    if len(args) > 1:
        if args[1] == 'cut_date': user_data['date'] = False
        if args[1] == 'cut_time': user_data['time'] = False
        if args[1] == 'cut_master': user_data['master'] = False
        if args[1] == 'cu_procedure': user_data['procedure'] = False
        if args[1] == 'cut_phone':
            user_data['phone'] = False
            user_data['time'] = False

    if call.data == 'about':about(call.message)
    if call.data == 'choose_master': choose_master(call.message)
    if call.data.startswith('main_menu'): main_menu(call.message)
    if call.data.startswith('master'): choose_date(call.message, master=int(args[1]))
    if call.data.startswith('re_choose_date'): choose_date(call.message)
    if call.data.startswith('choose_time'): choose_time(call.message, args[1])
    if call.data.startswith('re_choose_time'): choose_time(call.message)
    if call.data.startswith('confirmation'): confirmation(call.message, args[1])

    if call.data == 'choose_procedure': choose_procedure(call.message)
    if call.data.startswith('procedure'): choose_date(call.message, procedure=int(args[1]))

    if call.data.startswith('successful_booking'): successful_booking(call.message)

    if call.data == 'send_feedback': send_feedback(call.message)


def about(message):
    dialogue_text = 'Студия BeautyCity' + '\n'
    dialogue_text += 'Instagram: @BeautyCity' + '\n'
    dialogue_text += 'Vkontakte: vk.com/BeautyCity' + '\n'

    markup = types.InlineKeyboardMarkup(row_width=1)
    button_1 = types.InlineKeyboardButton("Посетить сайт - beautycity.ru", url='https://www.beautycity.ru')
    button_back = types.InlineKeyboardButton('<< Назад', callback_data='main_menu')

    markup.add(button_1, button_back)
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)


def send_feedback(message):
    user_data = bot.__dict__['users'][message.chat.id]

    dialogue_text = 'Будем Вам очень благодарны' + '\n'
    dialogue_text += 'за любой оставленный отзыв' + '\n\n'
    dialogue_text += 'Для этого, просто отправьте в чат' + '\n'
    dialogue_text += 'все те слова, которые хотели бы оставить' + '\n\n'

    markup = types.InlineKeyboardMarkup(row_width=1)
    button_back = types.InlineKeyboardButton('<< Назад', callback_data='main_menu')

    markup.add(button_back)
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)
    user_data.update({'last_message_id': message.id})
    bot.register_next_step_handler(message, add_feedback_to_db)


def choose_master(message):
    dialogue_text = 'Выберите мастера:'
    buttons = []
    for item in get_masters_name_from_base().values():
        buttons.append(types.InlineKeyboardButton(text=item['name'], callback_data=f'master#{item["id"]}'))

    markup = types.InlineKeyboardMarkup(row_width=3)
    for i in range(0, len(buttons), 3):
        markup.add(*buttons[i:i+3])
    markup.row(types.InlineKeyboardButton('<< Назад', callback_data='main_menu#cut_master'))
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)


def choose_procedure(message):
    dialogue_text = 'Выберите процедуру:'
    markup = types.InlineKeyboardMarkup(row_width=1)
    for item in get_services_from_base().values():
        markup.add(types.InlineKeyboardButton(
            text=f'{item["title"]} - {item["price"]}р.',
            callback_data=f'procedure#{item["id"]}'
            ))
    markup.add(types.InlineKeyboardButton('<< Назад', callback_data='main_menu#cut_procedure'))
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)


def choose_date(message, master=None, procedure=None):

    user_data = bot.__dict__['users'][message.chat.id]
    if master:
        user_data.update({'master': get_masters_name_from_base()[master]})
    else:
        master = user_data['master']

    if procedure:
        user_data.update({'procedure': get_services_from_base()[procedure]})
    else:
        procedure = user_data['procedure']

    if (user_data['master']):
        back_button = types.InlineKeyboardButton('<< Назад', callback_data='choose_master')
    else:
        back_button = types.InlineKeyboardButton('<< Назад', callback_data='choose_procedure')

    buttons = []
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    today = datetime.datetime.now().date()
    days_to_end_of_next_week = 14 - today.weekday()

    for i in range(days_to_end_of_next_week):
        new_date = today + datetime.timedelta(days=i)
        formatted_date = f"{new_date.day:02d}.{new_date.month:02d} ({days[new_date.weekday()]})"
        buttons.append(types.InlineKeyboardButton(formatted_date, callback_data=f'choose_time#{formatted_date}'))

    dialogue_text = print_booking_text(user_data)
    dialogue_text += 'Выберите удобный Вам день:'

    markup = types.InlineKeyboardMarkup(row_width=3)
    for i in range(0, len(buttons), 3):
        markup.add(*buttons[i:i+3])

    markup.row(back_button)
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)


def choose_time(message, date=None):

    user_data = bot.__dict__['users'][message.chat.id]
    if date:
        user_data.update({'date': date})
    else:
        date = user_data['date']

    dialogue_text = print_booking_text(user_data)
    dialogue_text += 'Выберите доступное время:'

    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []

    if user_data['master']:
        free_time = get_free_time_for_master(client_date=date, master_id=user_data['master']['id'])
    else:
        free_time = get_free_time_for_procedure(client_date=date)

    for item in free_time:
        buttons.append(types.InlineKeyboardButton(item, callback_data=f'confirmation#{item}'))

    for i in range(0, len(buttons), 4):
        markup.add(*buttons[i:i+4])
    markup.row(types.InlineKeyboardButton('<< Назад', callback_data='re_choose_date#cut_date'))
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)


def confirmation(message, time=None):

    user_data = bot.__dict__['users'][message.chat.id]
    if time:
        user_data.update({'time': time})
        user_data.update({'last_message_id': message.id})
    else:
        time = user_data['time']

    dialogue_text = print_booking_text(user_data)

    if user_data['first_time']:
        dialogue_text += 'Отправьте в чат, свой контактный номер.\n\n'
        dialogue_text += 'Отправляя нам свой телефон, Вы подтверждаете своё согласие на обработку Ваших данных.\n'
        dialogue_text += 'Более подробно с текстом соглашения можно ознакомиться по ссылке: www.confirmation.ru'

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.row(types.InlineKeyboardButton('<< Назад', callback_data='re_choose_time#cut_time'))
        bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)
        user_data['waiting_for_phone'] = True
        bot.register_next_step_handler(message, get_phone)
    else:
        dialogue_text += f'Ваш номер для связи: {user_data["phone"]}' + '\n\n'
        dialogue_text += 'Подтвердите Ваши контактные данные,\n'
        dialogue_text += 'или отправьте в чат, другой номер для связи.\n\n'

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.row(types.InlineKeyboardButton('Подтвердить Контактный Телефон', callback_data='successful_booking'))
        markup.row(types.InlineKeyboardButton('<< Назад', callback_data='re_choose_time#cut_time'))
        bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)
        user_data['waiting_for_phone'] = True
        bot.register_next_step_handler(message, get_phone)


def successful_booking(message):
    user_data = bot.__dict__['users'][message.chat.id]
    user_data['waiting_for_phone'] = False
    if user_data['first_time']:
        username = f'{message.chat.first_name} {message.chat.last_name}({message.chat.username})'
        username = username.replace(' None', '')
        username = username.replace('None', '')
        sql_register_new_user(message.chat.id, username, user_data['phone'])
    else:
        sql_put_user_phone(message.chat.id, user_data['phone'])

    dialogue_text = print_booking_text(user_data, not_confirmed=False)
    dialogue_text += f'Ваш номер для связи: {user_data["phone"]}' + '\n\n'
    date_for_sql_query = restoring_user_date_for_sql_query(user_data['date'])

    if user_data['master']:
        registration_new_appointment(
            date_for_sql_query,
            user_data['time'],
            message.chat.id,
            master_id=user_data['master']['id']
            )
    else:
        registration_new_appointment(
            date_for_sql_query,
            user_data['time'],
            message.chat.id,
            service_id=user_data['procedure']['id']
            )
    bot.send_message(message.chat.id, dialogue_text)
    bot.delete_message(message.chat.id, user_data['last_message_id'])
    start_menu(message)


# Добавление кнопки "позвонить нам" в ReplyKeyboardMarkup
@bot.message_handler(content_types=['text'])
def call_us(message):
    user_data = bot.__dict__['users'][message.chat.id]

    if user_data.get('waiting_for_phone', False):
        get_phone(message)
    elif "позвонить нам" in message.text.lower():
        bot.send_message(message.chat.id, "Рады звонку в любое время – 8 800 555 35 35")
        user_data['phone_button_state'] = False
        time.sleep(1)


def get_phone(message):
    user_data = bot.__dict__['users'][message.chat.id]
    if 'позвонить нам' not in message.text.lower():
        user_data.update({'phone': message.text})
        user_data['waiting_for_phone'] = False

        dialogue_text = print_booking_text(user_data)
        dialogue_text += f'Ваш номер для связи: {user_data["phone"]}' + '\n\n'
        dialogue_text += f'Подтвердите запись, или введите другой телефон для связи'

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.row(types.InlineKeyboardButton('Подтвердить Контактный Телефон', callback_data='successful_booking'))
        markup.row(types.InlineKeyboardButton('<< Назад', callback_data='re_choose_time#cut_phone'))
        try:
            bot.edit_message_text(dialogue_text, message.chat.id, user_data['last_message_id'], reply_markup=markup)
            bot.register_next_step_handler(message, get_phone)
            time.sleep(2)
            bot.delete_message(message.chat.id, message.id)
        except Exception as error:
            print(error)


def add_feedback_to_db(message):
    user_data = bot.__dict__['users'][message.chat.id]
    dialogue_text = 'Ваш отзыв:' + '\n'
    dialogue_text += message.text + '\n\n'
    dialogue_text += 'Принят!' + '\n'
    dialogue_text += 'Большое Вам Спасибо!!!'

    bot.send_message(message.chat.id, dialogue_text)
    sql_add_feedback(
        get_past_appointment(user_data['user_id']['id']),
        user_data['user_id']['id'],
        message.text
        )
    time.sleep(3)
    start_menu(message)


if __name__ == '__main__':
    print()
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f'Infinity polling exception: {e}', exc_info=True)
        time.sleep(5)  # Ожидание перед повторным запуском опроса
