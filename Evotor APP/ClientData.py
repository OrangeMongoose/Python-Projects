from Classes import MainClass
import os.path


class ClientData(MainClass):
    """
    Opening, reading and checking data from Config.ini file
    Class ClientData(MainClass)
        def self_check(self)
        def get_data(self)
    """
    def __init__(self):
        super().__init__()
        self.name = 'class ClientData(MainClass)'
        self.description = 'Считывание и проверка данных пользователя из файла настроек Config.ini'
        self.config_name = 'Config.ini'
        self.config_path = f'{os.path.abspath("")}{self.config_name}'
        self.data = {}
        self.lines_in_config = (
            'Client_UUID',
            'server',
            'database',
            'username',
            'password',
            'table',
            'select'
        )

    def self_check(self):
        wrong_values = (None, '', '\n')
        wrong_keys = []
        for key in self.data:
            if (key not in self.lines_in_config) or (self.data[key] in wrong_values):
                self.error['text'] = f'Не верная строка конфигурации - {key} : {self.data[key]}'
                self.error['status'] = True
                self.error['sys_ex'] = None
                return self.error

        for key in self.lines_in_config:
            if key not in self.data.keys():
                wrong_keys.append(key)
        if wrong_keys:
            self.error['text'] = f'Отсутствуют строки конфигурации - {[key for key in wrong_keys]}'
            self.error['status'] = True
            self.error['sys_ex'] = None
            return self.error

        self.message['text'] = 'Файл конфигурации прочитан'
        self.message['status'] = True
        return self.data

    def get_data(self):
        try:
            with open(self.config_name, 'r', encoding='utf-8') as f:
                for line in f:
                    if (not ('#' in line)) and (line != '\n') and (len(line.strip()) != 0):
                        key = line[0: line.find(':')].strip()
                        value = line[line.find(':') + 1: len(line)].strip()
                        self.data[key] = value
            f.close()
            return self.self_check()

        except FileNotFoundError as ex:
            self.error['text'] = f'Файл конфигурации {self.config_path}\\{self.config_name} не найден или поврежден'
            self.error['sys_ex'] = ex
            self.error['status'] = True
            return self.error
