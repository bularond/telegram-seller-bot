# -*- coding: utf-8 -*-

import logging

from settings import token, qiwi_account
from database import database
from qiwi import qiwi

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, 
                          CallbackQueryHandler, ConversationHandler,
                          PicklePersistence)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

MENU, CHOOSING, LOOKING, BUY, KEY, CHECK, LOOKING_KEYS = range(7)

db = database()
payments = qiwi()

menu_keyboard = [
    [InlineKeyboardButton("Каталог", callback_data='catalog')],
    [InlineKeyboardButton("Мои покупки", callback_data='purchases')],
    [InlineKeyboardButton("Гарантии", callback_data='warranty')],
    [InlineKeyboardButton("Отзывы", url="https://google.com")],
    [InlineKeyboardButton("Поддержка", url="https://yandex.ru")]
]
menu_markup= InlineKeyboardMarkup(menu_keyboard, one_time_keyboard=True)

def start(update, context):
    update.message.reply_text(
        "Главное меню",
        reply_markup=menu_markup
    )

    return MENU

def start_over(update, context):
    querry = update.callback_query

    context.bot.edit_message_text(
        chat_id=querry.message.chat_id,
        message_id=querry.message.message_id,
        text="Главное меню",
        reply_markup=menu_markup
    )

    return MENU

def warranty(update, context):
    querry = update.callback_query
    text = "✅ Гарантии\n"\
           "Наш проект молод и в него вложенно много сил, по этому в наших интересах предоставлять вам качественные услуги.\n\n"\
           "Мы несем ответсвенность за каждый проданный нами продукт, по этому гарантируем вам:\n"\
           "✅Качество проданного продукта, работоспособность заявленных характеристик.\n"\
           "✅Своевременную работу поддержки\n\n"\
           "При возникновении любых вопросов, обратитесь в поддержку, мы вам поможем!"

    context.bot.edit_message_text(
        chat_id=querry.message.chat_id,
        message_id=querry.message.message_id,
        text=text,
        reply_markup=menu_markup
    )

    return MENU

def catalog(update, context):
    querry = update.callback_query
    if(context.user_data.get('offset') == None):
        context.user_data['offset'] = 0
    items = db.get_catalog(offset=context.user_data['offset'])
    if(len(items)):
        reply_text = 'Список:\n'
        point = 1
        for item in items:
            reply_text += f"{point}. {item[1]} - {item[3]} p.\n"
            point += 1
        keyboard = list()
        for i in range(1, point, point//2):
            keyboard.append([])
            for j in range(i, min(point, i + point//2)):
                callback_data = str(items[j-1][0])
                keyboard[-1].append(InlineKeyboardButton(str(j), callback_data=callback_data))
        keyboard.append([
            InlineKeyboardButton('Назад', callback_data='back')
        ])
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        text = "Каталог пока пуст, но скоро в нем появятся новые товары. Обязательно возвращайтесь."
        keyboard = [
            [InlineKeyboardButton('Назад', callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.edit_message_text(
        chat_id=querry.message.chat_id,
        message_id=querry.message.message_id,
        text=reply_text,
        reply_markup=reply_markup
    )

    return CHOOSING


def product(update, context):
    querry = update.callback_query
    if(querry.data == 'back'):
        id = context.user_data['last_id']
    else:
        id = int(querry.data)
        context.user_data['last_id'] = id
    item = db.get_product_by_id(id)
    reply_text = f"{item[1]}\n{item[2]}\n{item[3]} p."
    keyboard = [
        [InlineKeyboardButton("Перейти к оплате", callback_data='buy')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_text(
        chat_id=querry.message.chat_id,
        message_id=querry.message.message_id,
        text=reply_text,
        reply_markup=reply_markup
    )

    return LOOKING

def buy(update, context):
    querry = update.callback_query
    item = db.get_product_by_id(context.user_data['last_id'])
    code = db.has_purchase(querry.message.chat_id, item[0])
    if(code == None):
        code = db.add_purchase(querry.message.chat_id, item[0])
    text  = f"К оплате {item[3]} рублей.\n"\
            f"Чтобы получить ключ переведите деньги на счет qiwi.com/p/{qiwi_account}.\n"\
            f"В коментариях укажите {code}.\n\n"
    keyboard = [
        [InlineKeyboardButton("Проверить оплату", callback_data=f'{code}')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_text(
        chat_id=querry.message.chat_id,
        message_id=querry.message.message_id,
        text=text,
        reply_markup=reply_markup
    )
    return BUY

def check(update, context):
    querry = update.callback_query
    code = int(querry.data)
    purchase = db.get_purchase_by_code(code)
    product = db.get_product_by_id(purchase[2])
    status = payments.check_payment(code, product[3])
    if(status == 2): # sucksess
        key = db.get_key_by_product_id(product[0])
        db.remove_purcases_by_code(code)
        db.remove_key(key[2])
        db.add_key_to_user(key[2], querry.message.chat_id)
        text  = f"Покупка прошла успешно.\n\n"\
                f"Ваш ключ {key[2]}.\n\n"\
                f"Вы так же сможете посмотреть его в разделе Мои покупки."
        keypad = [
            [InlineKeyboardButton("Назад", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keypad)
        context.bot.edit_message_text(
            chat_id=querry.message.chat_id,
            message_id=querry.message.message_id,
            text="```123123``` ***123321321123***",
            parse_mode="Markdown"
        )
        context.bot.send_message(
            chat_id=querry.message.chat_id,
            text=text,
            reply_markup=reply_markup
        )

    else: # unsucksess
        if(status == 1):
            text  = f"К оплате {product[3]} рублей.\n"\
                    f"Чтобы получить ключ переведите деньги на счет qiwi.com/p/{qiwi_account}.\n"\
                    f"В коментариях укажите {code}.\n\n"\
                    f"Оплата прошла неудачно."\
                    f"Если вы оплатили, то, пожалуйста, обратитесь в поддержку.\n\n"
            keypad = [
                [InlineKeyboardButton("Проверить оплату", callback_data=f'{code}')],
                [InlineKeyboardButton("Назад", callback_data='back')],
                [InlineKeyboardButton("Поддержка", callback_data='support')]
            ]
        elif(status == 0):
            text  = f"К оплате {product[3]} рублей.\n"\
                    f"Чтобы получить ключ переведите деньги на счет qiwi.com/p/{qiwi_account}.\n"\
                    f"В коментариях укажите {code}.\n\n"\
                    f"Вашей оплаты не найдено."\
                    f"Если вы оплатили, то, пожалуйста, обратитесь в поддержку."
            keypad = [
                [InlineKeyboardButton("Проверить оплату", callback_data=f'{code}')],
                [InlineKeyboardButton("Назад", callback_data='back')],
                [InlineKeyboardButton("Поддержка", callback_data='support')]
            ]
        reply_markup = InlineKeyboardMarkup(keypad)
        context.bot.edit_message_text(
            chat_id=querry.message.chat_id,
            message_id=querry.message.message_id,
            text=text,
            reply_markup=reply_markup
        )

    return CHECK

  
def purchases(update, context):
    querry = update.callback_query
    keys = db.get_users_keys(querry.message.chat_id)
    if(len(keys) == 0):
        text = "Вы пока не совершали покупки"
    else:
        text = "Ваши купленные ключи:\n"
        for key in keys:
            text += f"{key[1]}\n"
    keypad = [
        [InlineKeyboardButton("Назад", callback_data='back')],
    ]
    reply_markup = InlineKeyboardMarkup(keypad)
    context.bot.edit_message_text(
        chat_id=querry.message.chat_id,
        message_id=querry.message.message_id,
        text=text,
        reply_markup=reply_markup
    )

    return LOOKING_KEYS


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    pp = PicklePersistence(filename='users_states')

    updater = Updater(token, persistence=pp, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            MENU: [
                CallbackQueryHandler(catalog, pattern='^catalog$'),
                CallbackQueryHandler(purchases, pattern='^purchases$'),
                CallbackQueryHandler(warranty, pattern='^warranty$')
            ],
            LOOKING_KEYS: [
                CallbackQueryHandler(start_over, pattern='^back$')
            ],
            CHOOSING: [
                CallbackQueryHandler(start_over, pattern='^back$'),
                CallbackQueryHandler(product, pattern='')
            ],
            LOOKING: [
                CallbackQueryHandler(catalog, pattern='^back$'),
                CallbackQueryHandler(buy, pattern='^buy$')
            ],
            BUY: [
                CallbackQueryHandler(product, pattern='^back$'),
                CallbackQueryHandler(check, pattern='')
            ],
            CHECK: [
                CallbackQueryHandler(product, pattern='^back$'),
                CallbackQueryHandler(check, pattern=''),
            ]
        },

        fallbacks=[],
        name="seller_bot",
        persistent=True,
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

