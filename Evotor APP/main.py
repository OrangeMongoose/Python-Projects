#!\usr\bin\dev python 3
# -*- coding: utf-8 -*-

import requests
import pyodbc
import urllib.request
import xml.etree.ElementTree as ET
from operator import itemgetter
from datetime import datetime
import json
import logging
import os.path

external_products_from_DB = False    # Если False забирает данные из Deephouse.pro


def err_exit(logger):
    print_log_message(logger, 'Работа программы завершена из-за ошибки')
    exit(1)


def response_errors(logger, error_code, url):

    if error_code == 400:
        print_log_message(logger,
                          'При добавлении/изменении товаров в облако Эвотор возникла ошибка - '
                          'Неправильный синтаксис запроса, обратитесь к разработчику программы')
        err_exit(logger)

    elif error_code == 401:
        print_log_message(logger,
                          'Ошибка авторизации приложения. '
                          'Проверьте токен пользователя облака Эвотор в файле config.ini')
        err_exit(logger)

    elif error_code == 402:
        print_log_message(logger,
                          'Облако передаёт ошибку с кодом 402, в случае, когда происходит попытка обмена '
                          'данными между смарт-терминалами, привязанными к одному магазину, но приложение '
                          'не установлено на одно или несколько устройств или количество устройств в магазине '
                          'превышает количество устройств, оплаченных в приложении.')
        err_exit(logger)

    elif error_code == 403:
        print_log_message(logger,
                          'Нет доступа. Ошибка возникает когда у приложения нет разрешения на запрашиваемое действие '
                          'или пользователь не установил приложение в Личном кабинете.')
        err_exit(logger)

    elif error_code == 404:
        print_log_message(logger,
                          f'Неправильный адрес запроса к облаку Эвотор - {url}'
                          f' обратитесь к разработчику программы')
        err_exit(logger)

    elif error_code == 405:
        print_log_message(logger,
                          'При добавлении/изменении товаров в облако Эвотор возникла ошибка - '
                          'Ресурс не поддерживает использованный метод, обратитесь к разработчику программы')
        err_exit(logger)

    elif error_code == 406:
        print_log_message(logger,
                          'Тип содержимого, которое возвращает ресурс не соответствует типу содержимого, '
                          'которое указанно в заголовке Accept, обратитесь к разработчику программы')
        err_exit(logger)

    elif error_code == 413:
        print_log_message(logger,
                          'При добавлении/изменении товаров в облако Эвотор возникла ошибка - '
                          'Превышен максимальный объём запроса — 5 Мб')
        err_exit(logger)

    elif error_code == 429:
        print_log_message(logger,
                          'Превышено максимальное количество запросов к облаку Эвотор в текущем периоде. '
                          'Работу с ресурсом можно возобновить через 30 минут. '
                          'Время возобновления работы может быть изменено разработчиками Эвотор '
                          'без уведомления пользователей.')
        err_exit(logger)

    else:
        print_log_message(logger, f'Возникла неизвестная ошибка. Код ошибки: {error_code}')
        err_exit(logger)


def get_client_data(logger):
    client_data = {}
    config_name = 'Config.ini'
    try:
        with open(config_name, 'r', encoding="utf-8") as f:
            for line in f:
                if (not ("#" in line)) and (line != '\n') and (len(line.strip()) != 0):
                    key = line[0: line.find(':')].strip()
                    value = line[line.find(':') + 1: len(line)].strip()
                    client_data[key] = value
        f.close()

    except FileNotFoundError as ex:
        print_log_message(logger, f'Файл конфигурации {os.path.abspath("")}\\{config_name} не найден или поврежден')
        err_exit(logger)

    wrong_values = (None, '', '\n')
    wrong_keys = []
    lines_in_config = (
        'Client_UUID',
        'server',
        'database',
        'username',
        'password',
        'table',
        'select'
    )

    for key in client_data:
        if (key not in lines_in_config) or (client_data[key] in wrong_values):
            print_log_message(logger, f'Не верная строка конфигурации - {key} : {client_data[key]}')
            err_exit(logger)

    for key in lines_in_config:
        if key not in client_data.keys():
            wrong_keys.append(key)
    if wrong_keys:
        print_log_message(logger, f'Отсутствуют строки конфигурации - {[key for key in wrong_keys]}')
        err_exit(logger)

    print_log_message(logger, 'Файл конфигурации прочитан')
    return client_data


def get_store_uuid(logger, client_uuid):
    url = 'https://api.evotor.ru/api/v1/inventories/stores/search'
    headers = {
        'Authorization': client_uuid
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_response = response.json()
        return json_response[0]['uuid']
    else:
        response_errors(logger, response.status_code, url)


def get_data_evotor(logger, client_uuid):
    headers = {
        'Authorization': client_uuid
    }
    url = f'https://api.evotor.ru/api/v1/inventories/stores/{get_store_uuid(logger, client_uuid)}/products'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        products = []
        for product in response.json():
            element = {'code': int(product['code']), 'name': product['name'], 'price': float(product['price'])}
            products.append(element)
        products.sort(key=itemgetter('code'))
        return products
    else:
        response_errors(logger, response.status_code, url)


def get_data_mssql_db(logger, client_data):
    # 1 Подключаемся к БД
    try:
        connection_info = (
            f"DRIVER={{SQL Server Native Client 11.0}};"
            f"SERVER={client_data['server']};"
            f"DATABASE={client_data['database']};"
            f"UID={client_data['username']};"
            f"PWD={client_data['password']};"
            f"Trusted_Connection=yes;"
        )
        cnxn = pyodbc.connect(connection_info)
        cursor = cnxn.cursor()
        print_log_message(logger, "Успешное подключение к Базе Данных.")
    except:
        print_log_message(logger, f"Не удалось подключиться к Базе Данных {client_data['server']}")
        err_exit(logger)

    # 2 Забираем данные таблицы
    try:
        cursor.execute(client_data['select'].format(client_data['table']))
        result = []
        for row in cursor:
            element = {'code': int(row[1]), 'name': row[2], 'price': float(row[3])}
            result.append(element)
        print_log_message(logger, "Данные из Базы Данных получены успешно.")
        result.sort(key=itemgetter('code'))
        return result
    except:
        print_log_message(logger, f"Не удалось прочитать данные из таблицы {client_data['database']}.")
        err_exit(logger)
    finally:
        cnxn.commit()


def get_data_deephouse(logger):
    try:
        url = "http://deephouse.pro/upload/xml.xml"
        tree = ET.ElementTree(file=urllib.request.urlopen(url))
        yml_catalog = tree.getroot()
        price_list = yml_catalog[0][3]
        products = []
        for product in price_list:
            element = {'code': int(product.attrib['id']), 'name': product[0].text, 'price': float(product[1].text)}
            products.append(element)
        products.sort(key=itemgetter('code'))
        print_log_message(logger, f"Данные из {url} получены успешно.")
        return products
    except:
        print_log_message(logger, f"Не удалось получить данные из {url}")
        err_exit(logger)


def get_codes(products):
    codes = []
    for product in products:
        codes.append(product['code'])
    return codes


def get_diff_codes(source, pending):
    codes = []
    for code in source:
        if code not in pending:
            codes.append(code)
    return codes


def get_prod_by_code(products, code):
    for product in products:
        if product['code'] == code:
            return product
    print(f"Код товара {code} не найден")
    return None


def get_data_add(products, codes):
    data = []
    for code in codes:
        product = get_prod_by_code(products, code)
        element = {
            'name': product['name'],
            'code': product['code'],
            'price': product['price'],
            'measure_name': 'шт',
            'tax': 'NO_VAT',
            'allow_to_sell': True,
            'id': product['code'],
            'cost_price': '0.0',
            'quantity': '0.0',
            'type': 'NORMAL'
        }
        data.append(element)
    return data


def get_data_del(codes):
    products_del = '?id='
    for code in codes:
        products_del += str(code) + ','
    return products_del[:-1:]   # Отсекаем последнюю запятую


def add_products_evotor(logger, data, client_uuid):
    def add_func(slice):

        url = f'https://api.evotor.ru/stores/{store_uuid}/products'
        headers = {
            'Authorization': client_uuid,
            'Content-Type': 'application/vnd.evotor.v2+bulk+json'
        }
        response = requests.put(url, headers=headers, data=json.dumps(slice))
        # Получаем id операции в облаке Эвотор
        # json_response = response.json()
        # bulk_id = json_response['id']
        # Получаем статус операции в облаке Эвотор
        # url = f'https://api.evotor.ru/bulks/{bulk_id}'
        # response = requests.get(url, headers=headers)
        # print(response.json())
        if response.status_code != 202:
            print_log_message(logger, "Не удалось добавить/заменить товары в облако Эвотор.")
            response_errors(logger, response.status_code, url)

    print_log_message(logger, "Производится добавление товаров в облако Эвотор")
    store_uuid = get_store_uuid(logger, client_uuid)
    while len(data) > 5000:
        add_func(data[:5000])
        del data[:5000]
    else:
        add_func(data)
    print_log_message(logger, "Товары успешно добавлены/заменены")


def del_products_evotor(logger, codes, client_uuid):

    def delete_func(slice):
        url = f'https://api.evotor.ru/stores/{store_uuid}/products/{slice}'
        headers = {
            'Authorization': client_uuid,
            'Content-Type': 'application/vnd.evotor.v2+json'
        }
        response = requests.delete(url, headers=headers)
        if response.status_code != 204:
            print_log_message(logger, 'Не удалось удалить товары из облака Эвотор')
            response_errors(logger, response.status_code, url)

    print_log_message(logger, "Производится удаление товаров из облака Эвотор")
    store_uuid = get_store_uuid(logger, client_uuid)

    while len(codes) > 100:
        products_del = get_data_del(codes[:100])
        delete_func(products_del)
        del codes[:100]
    else:
        products_del = get_data_del(codes)
        delete_func(products_del)
    print_log_message(logger, "Товары успешно удалены из облака Эвотор")


def del_product_evotor(logger, code, client_uuid):
    url = f'https://api.evotor.ru/stores/{get_store_uuid(client_uuid)}/products/{str(code)}'
    headers = {
        'Authorization': client_uuid,
        'Content-Type': 'application/vnd.evotor.v2+json'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print_log_message(logger, "Товар успешно удален из облака Эвотор.")
    else:
        print_log_message(logger, f"Не удалось удалить товар {code} из облака Эвотор")
        response_errors(logger, response.status_code, url)


def product_search(code, client_uuid):
    url = f'https://api.evotor.ru/stores/{get_store_uuid(client_uuid)}/products/{code}'
    headers = {
        'Authorization': client_uuid,
        'Content-Type': 'application/vnd.evotor.v2+json',
        'Accept': 'application/vnd.evotor.v2+json'
    }
    response = requests.get(url, headers=headers)
    return response


def print_log_message(logger, message):
    print(message)
    logger.info(message)


def main():
    # Засекаем время исполнения
    time_start = datetime.now()

    # Активируем логирование в log-файл
    logger = logging.getLogger(__name__)
    logger.setLevel('INFO')
    file_handler = logging.FileHandler('main_log.log')
    file_handler.setLevel('INFO')
    file_handler.setFormatter(logging.Formatter(f"%(asctime)s - %(message)s"))
    logger.addHandler(file_handler)

    print_log_message(logger, f'{"*"*30} Начало работы программы {"*"*30}')

    # Получаем данные пользователя и настроек сервера Базы данных пользователя
    client_data = get_client_data(logger)

    # Получаем данные из облака Эвотор и сайта Дипхаус
    products_evotor = get_data_evotor(logger, client_data['Client_UUID'])
    if external_products_from_DB:
        products_external = get_data_mssql_db(logger, client_data)
    else:
        products_external = get_data_deephouse(logger)

    # Получаем массив кодов товаров
    codes_evotor = get_codes(products_evotor)
    codes_external = get_codes(products_external)

    # Получаем массив кодов в Эвотор, которых нет в Дипхаус (для последующего удаления этих товаров из Эвотор)
    codes_del = get_diff_codes(codes_evotor, codes_external)

    # Получаем массив кодов в Дипхаус, которых нет в Эвотор (для последующего добавления этих товаров в Эвотор)
    codes_add = get_diff_codes(codes_external, codes_evotor)

    # Служебный вывод информации о подготовленных к операциям товаров
    print_log_message(logger, f'Количество товаров на добавление: {len(codes_add)}')
    print_log_message(logger, f'Количество товаров на удаление: {len(codes_del)}')
    print_log_message(logger, f'Количество товаров из внешнего источника: {len(products_external)}')
    print_log_message(logger, f'Количество товаров в облаке Эвотор: {len(products_evotor)}')

    # Удаляем товары из полученного массива товаров Эвотор, для последующей сверки с массивом товаров Дипхаус,
    # для выявления несовпадений цен или наименований
    for code in codes_del:
        for product in products_evotor:
            if product['code'] == code:
                products_evotor.remove(product)
    print_log_message(logger, f'Количество товаров Эвотор после удаления: {len(products_evotor)}')

    # Добавляем товары в полученный массив товаров Эвотор, для последующей сверки с массивом товаров Дипхаус,
    # для выявления несовпадений цен или наименований
    for code in codes_add:
        for product in products_external:
            if product['code'] == code:
                products_evotor.append(product)
    print_log_message(logger, f'Количество товаров Эвотор после добавления: {len(products_evotor)}')

    # Сверяем на несовпадающие записи два массива товаров измененный и дополненный Эвотор и оригинальный Дипхаус
    codes_not_equal = []
    for product in products_external:
        if product != get_prod_by_code(products_evotor, product['code']):
            codes_not_equal.append(product['code'])
    print_log_message(logger, f'Количество несовпадающих записей: {len(codes_not_equal)} из {len(products_evotor)}')

    # Выполняем запрос на добавление записей в облако Эвотор
    if len(codes_add) > 0:
        data = get_data_add(products_external, codes_add)
        add_products_evotor(logger, data, client_data['Client_UUID'])

    # Выполняем запрос на удаление записей в облако Эвотор
    if len(codes_del) > 1:
        del_products_evotor(logger, codes_del, client_data['Client_UUID'])
    elif len(codes_del) == 1:
        del_product_evotor(logger, codes_del[0], client_data['Client_UUID'])

    # Выполняем запрос на добавление несовпадающих записе в облако Эвотор
    if len(codes_not_equal) > 0:
        data = get_data_add(products_external, codes_not_equal)
        add_products_evotor(logger, data, client_data['Client_UUID'])

    # Контрольный вывод общего количества товаров в облаке Эвотор после всех операций
    products_evotor = get_data_evotor(logger, client_data['Client_UUID'])
    print_log_message(logger, f'Количество товаров в облаке Звотор после выполнения всех операций: {len(products_evotor)}')

    # Вывод помеченных для удаления товаров, которые не удалось удалить из облака Эвотор
    if len(products_evotor) > len(products_external):
        undelete_products = get_diff_codes(products_evotor, products_external)
        if undelete_products:
            print_log_message(logger, 'Обнаружены следующие неудаленные товары, помеченные для удаления: ')
            print_log_message(logger, [code['code'] for code in undelete_products])
            print_log_message(logger, 'Попробуйте удалить товары вручную, или обратитесь к разработчику')

    print_log_message(logger, 'Выполнение программы завершено')
    print_log_message(logger, f'Время выполнения: {datetime.now() - time_start}')


if __name__ == '__main__':
    main()
