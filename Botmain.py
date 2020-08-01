import telebot
import config
import numpy as np
import cv2, os
from PIL import Image
from pydub import AudioSegment
bot = telebot.TeleBot(config.token)
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)


os.makedirs(os.getcwd()+'/files/photos/', exist_ok=True)
os.makedirs(os.getcwd()+'/files/voices/', exist_ok=True)


def finding_face(path):
    global k
    k = 0
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    images = []
    for image_path in image_paths:
        gray = Image.open(image_path).convert('L')
        image = np.array(gray, 'uint8')
        faces = faceCascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            images.append(image[y: y + h, x: x + w])
        if images != []:
            k = 1
        else:
            k = 0
    return k


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, ты написал мне /start')
    bot.send_message(message.chat.id, 'Отправь мне картинку или аудиосообщение')


@bot.message_handler(content_types=['photo'])
def face_recognition(message):
    try:
        file_info = bot.get_file(message.photo[0].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src = os.getcwd() + '/files/photos/' + message.photo[0].file_id + '.jpg'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        o = finding_face(os.getcwd() + '/files/photos/')
        if o == 1:
            bot.send_message(message.chat.id, 'Лицо найдено, картинка сохранена')
        else:
            bot.send_message(message.chat.id, 'Лицо не найдено, картинка будет удалена')
            os.remove(src)

    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(content_types=['voice'])
def audio_saver(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        uid = str(message.chat.id)
        os.makedirs(os.getcwd() + '/files/voices/' + uid + '/', exist_ok=True)
        dest = os.getcwd() + '/files/voices/' + uid + '/'
        num = str((len([f for f in os.listdir(dest)
                   if os.path.isfile(os.path.join(dest, f))])))
        src = dest + message.voice.file_id + '.ogg'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        voice = AudioSegment.from_ogg(src)
        voice.export(dest+'audio_message_' + num + '.wav', format='wav', bitrate=512000)
        bot.send_message(message.chat.id, 'Аудиосообщение было сохранено и конвертировано')
        os.remove(src)
    except Exception as e:
        bot.reply_to(message, e)


bot.polling()
