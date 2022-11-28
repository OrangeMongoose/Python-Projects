#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import pyperclip
import requests


if len(sys.argv) == 4:
    param_url = sys.argv[1]
    param_key1 = sys.argv[2]
    param_key2 = sys.argv[3]
    param_json = pyperclip.paste()

    if param_json[0] in ('"', "'"):
        pyperclip.copy('В буфере обмена должен содержаться словарь jsonData без внешних ковычек')
        exit(1)

    headders = {
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    data = json.dumps(param_json)
    data = json.loads(data)

    try:
        resp = requests.post(url=param_url, headers=headders, auth=(param_key1, param_key2), data=data.encode('utf-8'))
        if resp.status_code == 200:
            res = json.loads(resp.text)
            pyperclip.copy(res['Model']['Url'])
            exit(0)
        else:
            pyperclip.copy(resp.status_code, resp.raise_for_status())
    except requests.exceptions.RequestException as err:
        pyperclip.copy(err)
        exit(1)
else:
    pyperclip.copy("Ошибка. Проверьте правильность заполнения аргументов. CCPResult.exe 'url' 'key1' 'key2'")
    exit(1)

