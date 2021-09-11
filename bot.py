import telebot
import random
import datetime
import json
import os
from pyowm import OWM
from geopy.geocoders import Nominatim
from pyowm.utils.config import get_default_config
from PIL import Image, ImageDraw, ImageFont
from threading import Thread

if not os.path.exists("users"):
    os.makedirs("users")
    print("\"users\" directory created...")
if not os.path.exists("logs"):
    os.makedirs("logs")
    print("\"logs\" directory created...")
if not os.path.isfile("users.txt"):
    open("users.txt",'w').close()
    print("\"users.txt\" file created...")

# configurating tokens
if not os.path.exists("tokens.json"):
    print("You must have tokens.json file with your tokens...")
    file = open('tokens.json', 'w')
    file.write("{\"tg\": \"YOUR_TELEGRAM_BOT_TOKEN\", \"owm\": \"YOUR_OWM_TOKEN\"}")
    file.close()
    print("Token file created. Please past your tokens. Program will shutdown...")
    exit()
file = open('tokens.json', 'r')
config = json.loads(file.read())
file.close()

# configurating tokens

try:
    telebot.apihelper.get_me(config['tg'])
except:
    print("TelegramAPI token error! Program will shut down!")
    exit()
bot = telebot.TeleBot(config['tg'])
print('Telegram bot api loaded...')


config_dict = get_default_config()
config_dict['language'] = 'ru'
try:
    OWM(config['owm'], config_dict).weather_manager().weather_at_place("Moscow")
except:
    print("OWM api token error! Program will shut down!")
    exit()



owm = OWM(config['owm'], config_dict)
mgr = owm.weather_manager()
print('OWM api loaded...')
gameArray = []
status = {}
winds = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "CЗ"]
sticker_pack = ['CAACAgIAAxkBAAIHKF7yTUVSJTAvb5-uPuRBDtuMFxquAALcxgEAAWOLRgyxtRIUSi4a_xoE',
                'CAACAgIAAxkBAAIHKV7yTUZxQis7c5RU_NhVm3xX3KLAAALdxgEAAWOLRgzrTyk77CMCURoE',
                'CAACAgIAAxkBAAIHKl7yTUbSeCZyo2J_QEGVS03LJiYPAALexgEAAWOLRgxUcf2Fq_sguRoE',
                'CAACAgIAAxkBAAIHK17yTUeGimwsHn0m8DnZd2Z-0IMJAALfxgEAAWOLRgwcRRMg1btjFxoE',
                'CAACAgIAAxkBAAIHLF7yTUivakhqDr9yEpUAAZ-8UoDc6wAC4MYBAAFji0YMSLHz-sj_JqkaBA',
                'CAACAgIAAxkBAAIHLV7yTUjuo0nJ1hhYMQx3W5qktbe_AALhxgEAAWOLRgzvmnzNp7-0ehoE']

print("!!!ALYOSHAA BOT STARTED SUCCESSFUL!!!")
def getUsers():
    users = []
    try:
        text_file = open("users.txt", "r", encoding="utf-8")
        data = text_file.readlines()
        i = 0
        for line in data:
            users.append(line.rstrip())
        return users
    except:
        pass


def isUserExists(id):
    try:
        text_file = open("users.txt", "r", encoding="utf-8")
        users = text_file.readlines()
        contains = False
        for line in users:
            if int(id) == int(line):
                contains = True
        return contains
    except BaseException:
        print('her')


def getweather(id, city):
    try:
        answer = """
Ветер: $2
Влажность: $3%
Температура: $4 °C
Облачность: $5%
Время: $6
        """
        observation = mgr.weather_at_place(city)
        w = observation.weather
        answer = answer.replace("$2",
                                str(w.wind()['speed']) + " м/c " + winds[int(((w.wind()['deg'] + 22.5) // 45) % 8)])
        answer = answer.replace("$3", str(w.humidity))
        answer = answer.replace("$4", str(w.temperature('celsius')['temp']))
        answer = answer.replace("$5", str(w.clouds))
        answer = answer.replace("$6", datetime.datetime.fromtimestamp(
            datetime.datetime.today().timestamp() + w.utc_offset).strftime("%H:%M:%S"))
        bot.send_message(id, w.detailed_status.capitalize())
        bot.send_message(id, answer)
        im = Image.open('icons/weather1.png')
        weather = Image.open('icons/' + w.weather_icon_name + '.png')
        im.paste(weather, (400, 20), weather)
        draw_text = ImageDraw.Draw(im)
        font = ImageFont.truetype("timesbd.ttf", 30)
        draw_text.text((10, 10), city, font=font, fill=('#4d4d4d'))
        draw_text.text((10, 60), w.detailed_status.capitalize(), font=font, fill=('#ed6e4d'))
        draw_text.text((10, 150), answer, font=font, fill=('#4d4d4d'))
        draw_text.text((30, 400), "Восход", font=font, fill=('#4d4d4d'))
        draw_text.text((360, 400), "Закат", font=font, fill=('#4d4d4d'))
        draw_text.text((20, 440),
                       datetime.datetime.fromtimestamp(w.sunrise_time('unix') + w.utc_offset).strftime("%H:%M:%S"),
                       font=font, fill=('#ed6e4d'))
        draw_text.text((350, 440),
                       datetime.datetime.fromtimestamp(w.sunset_time('unix') + w.utc_offset).strftime("%H:%M:%S"),
                       font=font, fill=('#ed6e4d'))

        im.save(str(id) + '.png')
        photo = open(str(id) + '.png', 'rb')
        bot.send_photo(str(id), photo)
        photo.close()
        os.remove(str(id) + '.png')

    except BaseException as exc:
        bot.send_message(id,
                         "Упс..произошла какая-то ошибка! Возможно ваш город не поддерживается, обратитесь к администрации /report ваше обращение")
        print(type(exc))  # the exception instance
        print(exc.args)  # arguments stored in .args
        print(exc)


def getProfile(id):
    text_file = open('users/' + str(id) + '.txt', 'r', encoding='utf-8')
    prof = json.loads(text_file.read())
    text_file.close()
    return prof


def setCity(user_id, location):
    try:
        #       cityName=(requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+dirtyCityName+'&key=AIzaSyCXmlfzhF2rx3Yz7GeWUhulAiJxHG5zkUM&language=ru').json()['results'])[0]['address_components'][0]['long_name']
        geolocator = Nominatim(user_agent="geoapiExercises")
        cityName = str(
            geolocator.reverse(str(location.latitude) + "," + str(location.longitude)).raw['address']['city'])
        text_file = open('users/' + str(user_id) + '.txt', 'r', encoding='utf-8')
        prof = json.loads(text_file.read())
        text_file.close()
        prof['city'] = cityName
        data = json.dumps(prof)
        text_file = open('users/' + str(user_id) + '.txt', 'w', encoding='utf-8')
        text_file.write(data)
        text_file.close()
        bot.send_message(user_id, 'Город установлен на ' + cityName)
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = telebot.types.KeyboardButton(text="/weather")
        keyboard.add(button_phone)
        bot.send_message(user_id, "Настройки успешно установлены!", reply_markup=keyboard)

    except Exception as exc:
        print(type(exc))  # the exception instance
        print(exc.args)  # arguments stored in .args
        print(exc)
        bot.send_message(user_id,
                         "Произошла ошибка, попробуйте уточнить название города, либо обратитесь к администрации - /report ваше сообщение")
    dict.pop(status, user_id)


def append_to_file(file_name, text):
    text_file = open(file_name, 'a', encoding='utf-8')
    text_file.write(text)
    text_file.close()


class knGame:
    def __init__(self, attacker, defender):
        self.isAccepted = False
        self.attacker = attacker
        self.defender = defender
        self.field = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.symbol = "X"
        self.mesa = 0
        self.mesd = 0


def log(message):
    now = datetime.datetime.today()
    print('[' + now.strftime("%d.%m.%Y-%H:%M:%S") + '] ' + bot.get_chat(message.chat.id).first_name + ' (' + str(
        message.chat.id) + '): ' + str(message.text))
    thread1 = Thread(target=append_to_file, args=(('logs/log ' + now.strftime("%d-%m-%Y" + '.txt')), (
                '[' + now.strftime("%d.%m.%Y-%H:%M:%S") + '] ' + bot.get_chat(message.chat.id).first_name + ' (' + str(
            message.chat.id) + '): ' + message.text + '\n'),))
    thread1.start()
    thread1.join()
    return


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@bot.message_handler(commands=['start'])
def start_message(message):
    log(message)
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = telebot.types.KeyboardButton(text="/weather")
    keyboard.add(button_phone)
    bot.send_message(message.chat.id,
                     'Привет, меня зовут Алёша, я - бот. У меня есть много классных функций. Заценишь? /help',
                     reply_markup=keyboard)
    bot.send_message(message.chat.id, 'Ваш id: ' + str(message.chat.id))
    data = {"id": message.chat.id, "city": None, "isEvening": None}
    isExist = False
    try:
        text_file = open('users/' + str(message.chat.id) + '.txt', 'r', encoding='utf-8')
        text_file.close()
        isExist = True
    except BaseException:
        print("nasdo")
    if not isExist:
        text_file = open('users/' + str(message.chat.id) + '.txt', 'w', encoding='utf-8')
        text_file.write(json.dumps(data))
        text_file.close()
    text_file = open('users/' + str(message.chat.id) + '.txt', 'r', encoding='utf-8')
    prof = json.loads(text_file.read())
    if prof['city'] == None:  # or prof['isEvening'] == None
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = telebot.types.KeyboardButton(text="/settings")
        keyboard.add(button_phone)
        bot.send_message(message.chat.id,
                         'У тебя не все настройки заполнены, заполни командой /settings!',
                         reply_markup=keyboard)
    text_file.close()

    text_file = open("users.txt", "r+", encoding="utf-8")
    users = text_file.readlines()
    contains = False
    for line in users:
        print(line)
        if message.chat.id == int(line):
            contains = True
    if not contains:
        users.append(str(message.chat.id) + '\n')
    text_file.close()
    text_file = open('users.txt', 'w', encoding='utf-8')
    text_file.writelines(users)
    text_file.close()

    log(message)


@bot.message_handler(commands=['users'])
def users_message(message):
    log(message)
    if dict.get(getProfile(message.chat.id), 'admin'):
        users = getUsers()
        mess = "first name --- chat id \n"
        for i in range(0, len(users)):
            try:
                mess += bot.get_chat(users[i]).first_name
                try:
                    mess += '(@' + bot.get_chat(users[i]).username + ')'
                except:
                    pass
                mess += " --- " + str(users[i]) + "\n"
            except:
                pass
        bot.send_message(message.chat.id, mess)


@bot.message_handler(commands=['random'])
def random_message(message):
    log(message)
    args = message.text.split(' ')
    if len(args) == 3:
        if RepresentsInt(args[1]) and RepresentsInt(args[2]) and int(args[2]) > int(args[1]):
            bot.send_message(message.chat.id, random.randint(int(args[1]), int(args[2])))
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIPwl585SgS3E7V4NT8AiRqvnl-d4pgAAIOAAOo4OkRfgyHGXx0Y5QYBA')
        else:
            bot.send_message(message.chat.id, 'Неверный ввод, пример: /random [number1] [number2]')
    else:
        bot.send_message(message.chat.id, random.randint(0, 100))
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIPwl585SgS3E7V4NT8AiRqvnl-d4pgAAIOAAOo4OkRfgyHGXx0Y5QYBA')


@bot.message_handler(commands=['info'])
def info_message(message):
    log(message)
    if dict.get(getProfile(message.chat.id), 'admin') == True:
        args = message.text.split(' ')
        if len(args) == 2:
            try:

                bot.send_message(message.chat.id, 'First name - ' + bot.get_chat(args[1]).first_name)
                if bot.get_chat(args[1]).last_name: bot.send_message(message.chat.id,
                                                                     'Last name - ' + bot.get_chat(args[1]).last_name)
                if bot.get_chat(args[1]).username: bot.send_message(message.chat.id,
                                                                    'Username - ' + bot.get_chat(args[1]).username)
            except BaseException:
                print('EXCEPTION')
                return


@bot.message_handler(commands=['direct'])
def direct_message(message):
    log(message)
    if dict.get(getProfile(message.chat.id), 'admin') == True:
        args = message.text.split(' ')
        if len(args) >= 3 and RepresentsInt(args[1]) and isUserExists(args[1]):
            try:
                mess = ""
                for i in range(2, len(args)):
                    mess += args[i] + " "
                bot.send_message(args[1], mess)
            except BaseException:
                print('EXCEPTION')
                return


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    log(message)
    if dict.get(getProfile(message.chat.id), 'admin') == True:
        args = message.text.split(' ')
        if len(args) >= 2:
            try:
                mess = ""
                for i in range(1, len(args)):
                    mess += args[i] + " "
                text_file = open("users.txt", "r", encoding="utf-8")
                users = text_file.readlines()
                contains = False
                for line in users:
                    try:
                        bot.send_message(line, mess)
                    except BaseException:
                        print('EXCEPTION in line ' + line)

            except BaseException:
                print('EXCEPTION')
                return


@bot.message_handler(commands=['weather'])
def weather_message(message):
    log(message)
    text_file = open("users/" + str(message.chat.id) + ".txt", "r", encoding="utf-8")
    city = json.loads(text_file.read())['city']
    text_file.close()
    bot.send_message(message.chat.id, "Берем погоду в городе: " + city)
    thread1 = Thread(target=getweather, args=(message.chat.id, city))
    thread1.start()
    thread1.join()


@bot.message_handler(commands=['settings'])
def settings(message):
    log(message)
    try:
        text_file = open('users/' + str(message.chat.id) + '.txt', 'r', encoding='utf-8')
        prof = json.loads(text_file.read())
        if dict.get(status, message.chat.id) == None or dict.get(status, message.chat.id) == 0:
            bot.send_message(message.chat.id, 'Отправь мне свою геолокацию:')
            status[message.chat.id] = 1
        text_file.close()
    except BaseException:
        bot.send_message(message.chat.id,
                         'Хмм, произошла ошибка, попробуйте сначала ввести /start, если ошибка повторилась, обратитесь к администратору - /report ')


@bot.message_handler(commands=['report'])
def report(message):
    log(message)
    args = message.text.split(' ')
    if len(args) >= 2:
        mess = ""
        for i in range(1, len(args)):
            mess += args[i] + " "
        try:
            text_file = open("users.txt", "r+", encoding="utf-8")
            users = text_file.readlines()
            for line in users:
                try:
                    if dict.get(getProfile(line.rstrip()), 'admin') == True:
                        bot.send_message(int(line), '[REPORT] ' + bot.get_chat(message.chat.id).first_name + '(' + str(
                            message.chat.id) + '): ' + mess)
                        print('[REPORT] ' + bot.get_chat(message.chat.id).first_name + '(' + str(
                            message.chat.id) + '): ' + mess)
                except:
                    pass
            text_file.close()

        except BaseException:
            print("Братан всё плохо")
        bot.send_message(message.chat.id, 'Сообщение отправлено!')
    else:
        bot.send_message(message.chat.id, 'Напишите текст обращения!')


@bot.message_handler(commands=['help'])
def help_message(message):
    log(message)
    bot.send_message(message.chat.id, '''
/start - Информация о боте
/help - Список доступных комманд
/random [number1] [number2] - Вывести рандомное число в указаных пределах (или если их нет от 0 до 100)
/tictactoe id - Предложить пользователю поиграть в крестики-нолики
/dice - кинуть игральные кости
/settings - Настроить прогноз погоды
/weather - Вывести погоду
/report - Обратится к администратору

Создатель - @sumjest
        ''')


@bot.message_handler(commands=['tictactoe'])
def tictactoe_message(message):
    log(message)
    args = message.text.split(' ')
    contains = False

    if len(args) == 2:
        if args[1] == 'cancel':
            for game in gameArray:
                if str(message.chat.id) == str(game.attacker):
                    bot.send_message(message.chat.id, 'Предложение отменено')
                    bot.send_message(game.defender, 'Пользователь отменил игру')
                    gameArray.pop(gameArray.index(game))
                    return
            bot.send_message(message.chat.id, 'Вы ничего не предлагали')
            return
        text_file = open('users.txt', 'r', encoding='utf-8')
        users = text_file.readlines()
        for line in users:
            if line == (args[1] + '\n'):
                contains = True
            elif args[1][0] == '@' and args[1][1:] == bot.get_chat(int(line)).username:
                contains = True
                args[1] = line[:len(line) - 1]
        if not contains:
            bot.send_message(message.chat.id, 'Пользователь с таким id не найден')
        else:
            for game in gameArray:
                if str(game.attacker) == str(message.chat.id):
                    bot.send_message(message.chat.id, 'Вы уже ведёте игру!')
                    return
                if str(game.defender) == str(args[1]):
                    bot.send_message(message.chat.id, 'Противник уже ведет игру!')
                    return
            gameArray.append(knGame(message.chat.id, args[1]))
            if bot.get_chat(args[1]).username:
                bot.send_message(message.chat.id, 'Вы бросили вызов пользователю ' + bot.get_chat(
                    args[1]).first_name + ' (@' + bot.get_chat(args[1]).username + ') в крестики нолики.')
            else:
                bot.send_message(message.chat.id, 'Вы бросили вызов пользователю ' + bot.get_chat(
                    args[1]).first_name + ' (' + args[1] + ') в крестики нолики.')
            bot.send_message(message.chat.id, 'Чтобы отменить - /tictactoe cancel')
            if bot.get_chat(message.chat.id).username:
                bot.send_message(args[1], 'Вам бросил вызов пользователь ' + bot.get_chat(
                    message.chat.id).first_name + ' (@' + bot.get_chat(
                    message.chat.id).username + ') в крестики нолики.')
            else:
                bot.send_message(args[1], 'Вам бросил вызов пользователь ' + bot.get_chat(
                    message.chat.id).first_name + ' (' + str(message.chat.id) + ') в крестики нолики.')
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text='Да', callback_data=10))
            markup.add(telebot.types.InlineKeyboardButton(text='Нет', callback_data=11))
            bot.send_message(args[1], text="Принимаем?", reply_markup=markup)
        text_file.close()
    else:
        bot.send_message(message.chat.id, 'Неверный ввод, попробуйте /tictactoe [id или @username]')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    isAccepted = False
    if call.data == '10':
        for game in gameArray:
            if str(game.defender) == str(call.message.chat.id):
                game.isAccepted = True
                isAccepted = True
                bot.send_message(call.message.chat.id, 'Отлично! Начинаем игру. Вы ходите \'O\'')
                bot.send_message(game.attacker, 'Отлично! Начинаем игру. Вы ходите \'X\'')
                markup = telebot.types.InlineKeyboardMarkup(row_width=3)
                for i in range(0, 3):
                    markup.add(telebot.types.InlineKeyboardButton(text=game.symbol, callback_data=i * 3 + 1),
                               telebot.types.InlineKeyboardButton(text=game.symbol, callback_data=i * 3 + 2),
                               telebot.types.InlineKeyboardButton(text=game.symbol, callback_data=i * 3 + 3))
                game.mesa = bot.send_message(game.attacker, text="""
1|2|3
4|5|6
7|8|9
                """, reply_markup=markup).message_id
                game.mesd = bot.send_message(game.defender, text="""
1|2|3
4|5|6
7|8|9
                                """).message_id
        if not isAccepted:
            bot.send_message(call.message.chat.id, 'Игра не найдена')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    elif call.data == '11':

        for game in gameArray:
            if str(game.defender) == str(call.message.chat.id):
                bot.send_message(game.attacker, 'Вашу игру отклонили.')
                bot.send_message(call.message.chat.id, 'Хорошо, отклоняю')
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
                gameArray.pop(gameArray.index(game))
                return
        bot.send_message(call.message.chat.id, 'Игра не найдена')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    elif RepresentsInt(call.data) and int(call.data) >= 1 and int(call.data) <= 9:
        isFound = False
        for game in gameArray:
            if (str(game.defender) == str(call.message.chat.id) or str(game.attacker) == str(
                    call.message.chat.id)) and game.isAccepted:
                isFound = True
                if game.field[int(call.data) - 1] == int(call.data):
                    game.field[int(call.data) - 1] = game.symbol;
                    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
                    if game.symbol == 'X':
                        text = ""
                        game.symbol = 'O'
                        for i in range(0, 3):
                            markup.add(telebot.types.InlineKeyboardButton(text=game.symbol, callback_data=i * 3 + 1),
                                       telebot.types.InlineKeyboardButton(text=game.symbol, callback_data=i * 3 + 2),
                                       telebot.types.InlineKeyboardButton(text=game.symbol, callback_data=i * 3 + 3))
                            text = text + str(game.field[i * 3]) + '|' + str(game.field[i * 3 + 1]) + '|' + str(
                                game.field[i * 3 + 2]) + "\n"

                        bot.delete_message(game.defender, game.mesd)
                        bot.delete_message(game.attacker, game.mesa);

                        game.mesa = bot.send_message(game.attacker, text=text).message_id
                        game.mesd = bot.send_message(game.defender, text=text, reply_markup=markup).message_id
                    else:
                        game.symbol = 'X'
                        text = ""
                        for i in range(0, 3):
                            markup.add(telebot.types.InlineKeyboardButton(text=game.symbol, callback_data=i * 3 + 1),
                                       telebot.types.InlineKeyboardButton(text=game.symbol, callback_data=i * 3 + 2),
                                       telebot.types.InlineKeyboardButton(text=game.symbol, callback_data=i * 3 + 3))
                            text = text + str(game.field[i * 3]) + '|' + str(game.field[i * 3 + 1]) + '|' + str(
                                game.field[i * 3 + 2]) + "\n"
                        bot.delete_message(game.attacker, game.mesa)
                        bot.delete_message(game.defender, game.mesd)
                        game.mesd = bot.send_message(game.defender, text=text).message_id
                        game.mesa = bot.send_message(game.attacker, text=text, reply_markup=markup).message_id

                    isNichya = True
                    test = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                    for i in range(0, 9):
                        if game.field[i] == 'X':
                            test[i] = 1;
                        elif game.field[i] == 'O':
                            test[i] = -1;
                        else:
                            isNichya = False
                    for i in range(0, 3):
                        sum = 0
                        dsum = 0
                        diag1 = 0
                        diag2 = 0
                        for j in range(0, 3):
                            sum += test[i * 3 + j]
                            dsum += test[j * 3 + i]
                            diag1 += test[j * 4]
                            diag2 += test[j * 2 + 2]
                        if (abs(sum) == 3 or abs(dsum) == 3 or abs(diag1) == 3 or abs(diag2) == 3):
                            if game.symbol == 'X':
                                bot.send_message(game.defender, 'Вы выиграли!')
                                bot.send_message(game.attacker, 'Вы проиграли!')
                                bot.edit_message_reply_markup(game.attacker, game.mesa)
                            else:

                                bot.send_message(game.attacker, 'Вы выиграли!')
                                bot.send_message(game.defender, 'Вы проиграли!')
                                bot.edit_message_reply_markup(game.defender, game.mesd)
                            gameArray.pop(gameArray.index(game))
                            return
                    if isNichya:
                        bot.send_message(game.defender, 'Ничья!')
                        bot.send_message(game.attacker, 'Ничья!')
                        gameArray.pop(gameArray.index(game))
                        if game.symbol == 'X':
                            bot.edit_message_reply_markup(game.attacker, game.mesd)
                        else:
                            bot.edit_message_reply_markup(game.defender, game.mesd)
                        return
                else:
                    return
        if not isFound:
            bot.send_message(call.message.chat.id, "Игра завершена")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


# elif RepresentsInt(call.data) and (int(call.data)==100 or int(call.data)==101):
#     print("sosi")
#     if dict.get(status,call.message.chat.id)==2:
#         text_file = open('users/' + str(call.message.chat.id) + '.txt', 'r', encoding='utf-8')
#        prof = json.loads(text_file.read())
#         text_file.close()
#         if int(call.data)==100:
#             prof['isEvening'] = True
#        else:
#             prof['isEvening'] = False

#         data = json.dumps(prof)
#         text_file = open('users/' + str(call.message.chat.id) + '.txt', 'w', encoding='utf-8')
#         text_file.write(data)
#         text_file.close()
#         bot.edit_message_reply_markup(call.message.chat.id,call.message.message_id)
#         dict.pop(status,call.message.chat.id)


@bot.message_handler(commands=['dice'])
def dice_message(message):
    log(message)
    if len(message.text.split(' ')) == 1:
        dice = random.randint(1, 6)
        bot.send_message(message.chat.id, 'Вы кинули кости и выпало: ' + str(dice))
        bot.send_sticker(message.chat.id, sticker_pack[dice - 1])
    else:
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        bot.send_message(message.chat.id, 'Вы кинули кости и выпало: ' + str(dice1 + dice2))
        bot.send_sticker(message.chat.id, sticker_pack[dice1 - 1])
        bot.send_sticker(message.chat.id, sticker_pack[dice2 - 1])


@bot.message_handler(content_types=['sticker'])
def sticker_message(message):
    message.text = '[sticker]: ' + message.sticker.file_id
    log(message)


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        message.text="[location]: latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude)
        log(message)
    if dict.get(status, message.chat.id) == 1:
        thread1 = Thread(target=setCity, args=(message.chat.id, message.location))
        thread1.start()
        thread1.join()


@bot.message_handler(content_types=['text'])
def just_message(message):
    log(message)


#    if dict.get(status,message.chat.id)==1:
#        thread1 = Thread(target=setCity,args=(message.chat.id,message.text))
#        thread1.start()
#       thread1.join()
#  markup = telebot.types.InlineKeyboardMarkup()
#  markup.add(telebot.types.InlineKeyboardButton(text="Да", callback_data=100),
#             telebot.types.InlineKeyboardButton(text="Нет", callback_data=101),
#             )
#  bot.send_message(message.chat.id, "Установить оповещения о погоде утром?",reply_markup=markup).message_id
#   status[message.chat.id]=2


bot.polling(True)
