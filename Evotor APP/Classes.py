class MainClass:
    """
    Meta-class with general methods and functions for logging

    class MainClass
        def get_error_status(self)
        def log_error(self)
        def get_message_status(self)
        def log_message(self)
        def get_description(self)
    """
    def __init__(self):
        self.name = 'Main Class'
        self.description = 'Корневой класс'
        self.error = {
            'text': None,
            'sys_ex': None,
            'status': False
        }
        self.message = {
            'text': None,
            'status': False
        }

    def get_error_status(self):
        return self.error['status']

    def log_error(self):
        return self.error['text']

    def get_message_status(self):
        return self.message['status']

    def log_message(self):
        return self.message['text']

    def get_description(self):
        return self.description
