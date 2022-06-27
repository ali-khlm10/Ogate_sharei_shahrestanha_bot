from telegram.ext import Updater, CommandHandler, callbackcontext, MessageHandler, CallbackQueryHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.chataction import ChatAction
from telegram.ext.filters import Filters


import requests
from bs4 import BeautifulSoup

import re

from uuid import uuid4
from telegram import error
import logging

FIRST, SECOND = range(2)
myDataDict = {}
bot_token = '5124672848:AAHgK0oshVeBCiIg9NbW8FQuR1AEVkRjKGg'

main_url = "https://badesaba.ir/owghat/{}/{}"

second_url = "https://badesaba.ir/convert-date"

Temp_1 = ''


def start_bot(update: Update, context=callbackcontext):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)

    if type(first_name) == str and type(last_name) == str:
        update.message.reply_text(
            text="سلام {} {} 🙋‍♂️\n\nبه ربات اعلام اوقات شرعی شهرستان های کشور خوش آمده اید.\n\nجهت ادامه روی دستور زیر کلیک کنید:\n\n\n\n/main_menu".format(first_name, last_name))
    else:
        update.message.reply_text(
            text='سلام {} 🙋‍♂️\n\nبه ربات اعلام اوقات شرعی شهرستان های کشور خوش آمده اید.\n\nجهت ادامه روی دستور زیر کلیک کنید:\n\n\n\n/main_menu'.format(first_name))


def main_menu_bot(update: Update, context=callbackcontext):
    buttons = [
        ('اوقات شرعی شهرستان ها',),
        ('راهنمایی',),
        ('تماس با ما',)
    ]
    update.message.reply_text(text='جهت اعلام اوقات شرعی از منوی زیر انتخاب کنید : ', reply_markup=ReplyKeyboardMarkup(
        buttons, resize_keyboard=True))


def provinces(update: Update, context=callbackcontext):
    a = update.message.reply_text(
        text='هر مرحله از عملیات ممکن است چند ثانیه طول بکشد، از صبوری شما متشکریم.')
    buttons = []
    provinces_persian_names = []
    provinces_english_names = []
    main_url = "https://badesaba.ir/owghat/map"
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    result_1 = soup.find_all(
        'div', class_='col-6 col-sm-4 p-1 ng-star-inserted')

    for item in result_1:
        provinces_persian_names.append(item.text.strip())
        provinces_english_names.append(re.sub(r'\D+=', '', item.a.get('href')))

    for i in range(0, len(provinces_persian_names)-1, 2):
        buttons.append([InlineKeyboardButton(
            f'{provinces_persian_names[i+j]}', callback_data=f'{provinces_english_names[i+j]}') for j in range(2)])

    buttons.append([InlineKeyboardButton(
        f'{provinces_persian_names[len(provinces_persian_names)-1]}', callback_data=f'{provinces_english_names[len(provinces_persian_names)-1]}')])

    update.message.reply_text(
        text='یکی از استان های زیر را جهت اعلام اوقات شرعی انتخاب کنید :', reply_markup=InlineKeyboardMarkup(buttons))

    context.bot.delete_message(chat_id=a.chat_id, message_id=a.message_id)
    return FIRST


def city(update: Update, context: callbackcontext):
    cities_name = []
    cities_id = []

    query = update.callback_query
    data = query.data
    print(data)

    global Temp_1
    Temp_1 = data

    chat_id = query.message.chat_id
    message_id = query.message.message_id

    main_url = "https://badesaba.ir/owghat/map?state={}"
    response = requests.get(main_url.format(data))
    soup = BeautifulSoup(response.content, 'html.parser')
    result_1 = soup.find_all(
        'div', class_='col-6 col-md-4 col-lg-3 col-xl-2 p-1 ng-star-inserted')

    for item in result_1:
        cities_id.append(re.search(r'\d{1,5}', item.a.get('href')).group())
        cities_name.append(item.text.strip())

    buttons = []
    temp = len(cities_name) % 2
    if temp == 0:
        for i in range(0, len(cities_name), 2):
            buttons.append([InlineKeyboardButton(
                f'{cities_name[i+j]}', callback_data=f'{cities_id[i+j]} {cities_name[i+j]}') for j in range(2)])
    else:
        for i in range(0, len(cities_name)-temp, 2):
            buttons.append([InlineKeyboardButton(
                f'{cities_name[i+j]}', callback_data=f'{cities_id[i+j]} {cities_name[i+j]}') for j in range(2)])

        buttons.append([InlineKeyboardButton(
            f'{cities_name[len(cities_name)-1]}', callback_data=f'{cities_id[len(cities_id)-1]} {cities_name[len(cities_name)-1]}')])

    context.bot.editMessageText(
        text='اوقات شرعی کدام شهرستان را نشون بدم : ', chat_id=chat_id,
        message_id=message_id, reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def end_weather(update: Update, context: callbackcontext):
    global myDataDict
    query = update.callback_query
    data = query.data
    print('sssss=', data)
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    myDataDict[chat_id] = data
    result = weather_func(data)
    context.bot.editMessageText(text='✅ شهر {} به عنوان شهر مورد نظر شما انتخاب شد.\n\n\n\n{}'.format(re.sub(r'\d+ ', '', myDataDict[chat_id]), result),
                                chat_id=chat_id, message_id=message_id)
    return ConversationHandler.END


def Help(update: Update, context: callbackcontext):
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    update.message.reply_text(text='با سلام و درود 🙋‍♂️\nاین ربات اوقات شرعی شهرستان های هر استان را به اطلاع شما می رساند.\n\
جهت اطلاع از اوقات شرعی شبانه روز شهر خود ابتدا از منوی اصلی روی گزینه ی "اوقات شرعی شهرستان ها" کلیک کنید تا لیست استان های کشور نمایش داده شود ، سپس روی استان موردنظر خود کلیک کنید تا لیست شهرستان های \
استان مورد نظر نمایش داده شود سپس روی شهرستان مورد نظر کلیک کنید تا اوقات شرعی آن را پس از چند ثانیه مشاهده کنید.\n\n✅توجه داشته باشید که در هر مرحله از عملیات ممکن است به خاطر ضعیف بودن اینترنت لیست استان ها\
 و شهرستان ها و نمایش اوقات شرعی کمی با تاخیر نمایش داده شود پس صبور باشید.\nبا تشکر از صبوری شما.')



def contact_us(update: Update, context: callbackcontext):
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    update.message.reply_text(text="در صورت بروز هرگونه مشکل در هر مرحله از عملیات ربات لطفا به ما اطلاع دهید.\nاگر پیشنهاد ،انتقاد و نظری دارید حتما به ما اطلاع دهید تا رسیدگی شود.\n\n\nآیدی ادمین ربات : \n\n@pro2020_40")


def weather_func(str):
    timeAndtext = ''
    response = requests.get(main_url.format(
        re.split(r" ", str)[0], re.split(r" ", str)[1]))
    soup = BeautifulSoup(response.content, 'html.parser')
    response_1 = requests.get(second_url)
    soup_1 = BeautifulSoup(response_1.content, 'html.parser')
    result_1 = soup.find('div', class_='col d-flex')
    result_2 = soup.find('span', class_='date-ghamary py-2')
    result_3 = soup.find('span', class_='date-milady font-en')
    result_4 = soup.find_all('div', class_='col-12 col-lg')
    result_5 = soup_1.find('div', class_='col-12 text-month mt-2')
    result_6 = soup_1.find('div', class_='col-12 text-date mt-2')
    timeAndtext += 'نزدیکترین اوقات شرعی : ' + result_4[0].find_all('p')[0].text + '\n\n\
🔹' + result_4[0].find_all('p')[2].text.strip()+':              ' + result_4[0].find_all('p')[1].text + ' 🕠\n\
🔹' + result_4[0].find_all('p')[4].text.strip()+':           ' + result_4[0].find_all('p')[3].text + ' 🕠\n\
🔹' + result_4[0].find_all('p')[6].text.strip()+':                ' + result_4[0].find_all('p')[5].text + ' 🕠\n\
🔹' + result_4[0].find_all('p')[8].text.strip()+':               ' + result_4[0].find_all('p')[7].text + ' 🕠\n\
🔹' + result_4[0].find_all('p')[10].text.strip()+':           ' + result_4[0].find_all('p')[9].text + ' 🕠\n\
🔹' + result_4[0].find_all('p')[12].text.strip()+':             ' + result_4[0].find_all('p')[11].text + ' 🕠\n\
🔹' + result_4[0].find_all('p')[14].text.strip()+':              ' + result_4[0].find_all('p')[13].text + ' 🕠\n\
🔹' + result_4[0].find_all('p')[16].text.strip()+':      ' + result_4[0].find_all('p')[15].text + ' 🕠\n\n\n\n@ogate_sharei_bot'

    return '⏳ '+result_1.h1.text.strip()+'\n\n\
'+'📆 تاریخ شمسی امروز : ' + result_5.text + result_6.text + '\n'+'📆 تاریخ قمری امروز :                     ' + result_2.text + '\n' + '📆 تاریخ میلادی امروز : \n\
     ' + result_3.text.strip() + '\n\n' + timeAndtext


def main():
    updater = Updater(bot_token, use_context=True)
# ////////////////////////////////////////////////////////////////////

    conversation = ConversationHandler(entry_points=[
        MessageHandler(Filters.regex('اوقات شرعی'), provinces)],
        states={
            FIRST: [
                CallbackQueryHandler(
                    city, pattern=Temp_1),
            ],
            SECOND: [CallbackQueryHandler(end_weather)],
    },
        fallbacks=[MessageHandler(Filters.regex('اوقات شرعی'), provinces)],
        allow_reentry=True
    )
    updater.dispatcher.add_handler(conversation)

# ////////////////////////////////////////////////////////////////////
    start_command = CommandHandler("start", start_bot)
    updater.dispatcher.add_handler(start_command)

    main_menu_command = CommandHandler("main_menu", main_menu_bot)
    updater.dispatcher.add_handler(main_menu_command)

    help_command = MessageHandler(
        Filters.regex('راهنمایی'), Help)
    updater.dispatcher.add_handler(help_command)

    contact_us_command = MessageHandler(
        Filters.regex('تماس با ما'), contact_us)
    updater.dispatcher.add_handler(contact_us_command)

# ////////////////////////////////////////////////////////////////////
    # print(Temp_1)
    updater.start_polling()
    updater.idle()


main()
