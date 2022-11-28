#!\usr\bin\dev python 3
# -*- coding: utf-8 -*-

import logging
import logging.config
import os.path
import Logger as app_logger



def main():
    logger = app_logger.get_logger(__name__, app_logger.log_format_short)
    logger.info('='*30 + ' Старт работы программы ' + '='*30)
    client_data = ClientData()
    client_data.get_data()
    if client_data.get_error_status():
        logger.error(client_data.get_error_text()['text'])
    elif client_data.message_status:
        logger.info(client_data.get_message())

    logger.info('=' * 30 + ' Работа программы завершена ' + '=' * 30)
    return 0


if __name__ == '__main__':
    main()
