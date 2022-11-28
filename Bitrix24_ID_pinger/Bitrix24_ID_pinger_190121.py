#!/usr/bin/python
#-*-coding: utf-8-*-

import sys
import requests
import ctypes
import json

urlpart1 = 'https://orangetech.bitrix24.ru/rest/1/x48fgi8a1o2zhvxj/im.notify?to='
urlpart2 = '&type=SYSTEM&message='
headers = {'Content-Type':"application/json", 'charset':'UTF-8'}

#-----------------------------------
def main(argh_userID, argh_userMSG):
    if not argh_userID.isdigit():
        msg_txt = 'Произошла ошибка связанная с именем пользователя: \n\nВозможно ID пользователя не число. Проверьте правильность ввода параметра. Текущее значение: ' + str(
            argh_userID) + '\n\nВыполнение программы прекращено.'
        msg_ttl = 'Ошибка передачи данных'
        ctypes.windll.user32.MessageBoxW(0, msg_txt, msg_ttl, 0)
        sys.exit(1)
    url = urlpart1 + str(argh_userID) + urlpart2 + str(argh_userMSG)
    try:
        url = requests.get(url, headers=headers)
        jstr = json.loads(url.text)
        if url.status_code == 400:
            if str(jstr['error'] == 'USER_ID_EMPTY'):
                msg_txt = 'Произошла ошибка связанная с именем пользователя: \n\nВозможно ID пользователя не число. Проверьте правильность ввода параметра. Текущее значение: ' + str(argh_userID) + '\n\nВыполнение программы прекращено.'
                msg_ttl = 'Ошибка передачи данных'
                ctypes.windll.user32.MessageBoxW(0, msg_txt, msg_ttl, 0)
                sys.exit(1)
        elif url.status_code == 200:
            if str(jstr['result']) == 'False':
                msg_txt = 'Произошла ошибка связанная с именем пользователя: \n\nВозвращен параметр False при попытке передачи сообщения пользователю: ' + str(argh_userID) + '\n\nВыполнение программы прекращено.'
                msg_ttl = 'Ошибка передачи данных'
                ctypes.windll.user32.MessageBoxW(0, msg_txt, msg_ttl, 0)
                sys.exit(1)
    except requests.exceptions.RequestException as err:
        msg_txt = 'Произошла ошибка обращения по адресу: ' + url + '\n\nПолный текст ошибки:\n\n' + str(err) + '\n\nВыполнение программы прекращено.'
        msg_ttl = 'Ошибка подключения'
        ctypes.windll.user32.MessageBoxW(0, msg_txt, msg_ttl, 0)
        sys.exit(1)
#-------------------------
if __name__ == '__main__':

    if len (sys.argv) == 3:
        param1 = str(sys.argv[1])
        param2 = str(sys.argv[2])
        sys.exit(main(param1, param2))
    else:
        if len (sys.argv) < 3:
            msg_ttl = 'Ошибка выполнения скрипта Bitrix_24_ID_pinger'
            msg_txt = 'Произошла ошибка - слишком мало параметров.\nПроверьте параметры вызова скрипта. Первым должен передаваться ID пользователя Bitrix24 (число), вторым передаваемое сообщение в двойных ковычках.\n\nВыполнение программы прекращено.'
            ctypes.windll.user32.MessageBoxW(0, msg_txt, msg_ttl, 0)
            sys.exit (1)

        if len (sys.argv) > 3:
            msg_ttl = 'Ошибка выполнения скрипта Bitrix_24_ID_pinger'
            msg_txt = 'Произошла ошибка - слишком много параметров.\nПроверьте параметры вызова скрипта. Первым должен передаваться ID пользователя Bitrix24(число), вторым передаваемое сообщение в двойных ковычках.\n\nВыполнение программы прекращено.'
            ctypes.windll.user32.MessageBoxW(0, msg_txt, msg_ttl, 0)
            sys.exit (1)
