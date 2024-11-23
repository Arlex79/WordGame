from datetime import datetime
from time import time
from colorama import init, Fore, Style

colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX,
          Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
          Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX,
          Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
          ]

SERV_MSG_COLOR = Fore.BLUE
NICK_COLOR_DEFAULT = Fore.LIGHTYELLOW_EX
TIME_COLOR = Fore.LIGHTBLACK_EX

TYPE_TO_CHAT_COLOR = Fore.WHITE
TYPE_WARNING_COLOR = Fore.LIGHTRED_EX
TYPE_ERROR_COLOR = Fore.RED
TYPE_INFO_COLOR = Fore.LIGHTWHITE_EX
TYPE_GAME_COLOR = Fore.GREEN
MSG_SMBL_PRE_COLOR = Fore.YELLOW
USER_MSG_COLOR = Fore.WHITE

init()


class Msg:

    def __init__(self, content='TEXT_DEFALULT', from_='server', type='to chat', time_1970=None):
        self.text = content
        self.from_ = from_
        self.type = type
        self.msg_sep = '<SEP>'
        if time_1970 == None:

            self.time = time()

        else:
            self.time = time_1970

        if from_ == None:
            self.from_ = 'server'

    def get_send_time(self):
        return datetime.fromtimestamp(self.time).strftime('%H:%M')  # '%m.%d.%Y %H:%M:%S'

    def is_for_print(self):
        if self.type == 'to chat' or self.type == 'warning' \
                or self.type == 'error' or self.type == 'info' or self.type == 'word game data' \
                or self.type == 'word info':
            return True
        return False

    def __repr__(self):
        string = f'''Msg(f"""{self.text}""", "{self.from_}", "{self.type}", {self.time}){self.msg_sep}'''
        return string

    def __str__(self):
        if self.from_.lower() != 'server':
            from_ = f' {self.from_}'
        else:
            from_ = ''

        if self.type == 'to chat':
            string = f'[CHAT] [{self.get_send_time()}]{from_}: {self.text}'

        elif self.type == 'warning':
            string = f'[!] [{self.get_send_time()}]{from_}: {self.text}'

        elif self.type == 'error':
            string = f'[ERR] [{self.get_send_time()}]{from_}: {self.text}'

        elif self.type == 'info':
            string = f'[I] [{self.get_send_time()}]{from_}: {self.text}'

        elif self.type == 'word game data':
            string = f'[GAME] [{self.get_send_time()}]{from_}: {self.text}'
        else:
            string = f'[NOT FOR PRINT! | type={self.type}] [{self.get_send_time()}]{from_}: {self.text}'

        return string

    def console_print_colored(self):
        if self.from_.lower() != 'server':
            from_ = f' {self.from_}'
        else:
            from_ = ''

        if self.type == 'to chat':
            string = f'%s[CHAT] %s[{self.get_send_time()}] %s{from_}%s: %s{self.text}' % \
                     (TYPE_TO_CHAT_COLOR, TIME_COLOR, NICK_COLOR_DEFAULT, MSG_SMBL_PRE_COLOR, USER_MSG_COLOR)

        elif self.type == 'warning':
            string = f'%s[!] %s[{self.get_send_time()}]%s: %s{self.text}' % \
                     (TYPE_WARNING_COLOR, TIME_COLOR, MSG_SMBL_PRE_COLOR, TYPE_WARNING_COLOR)

        elif self.type == 'error':
            string = f'%s[ERR] %s[{self.get_send_time()}]%s: %s{self.text}' % \
                     (TYPE_ERROR_COLOR, TIME_COLOR, MSG_SMBL_PRE_COLOR, SERV_MSG_COLOR)
        elif self.type == 'info':
            string = f'%s[I] %s[{self.get_send_time()}]%s: %s{self.text}' % \
                     (TYPE_INFO_COLOR, TIME_COLOR, MSG_SMBL_PRE_COLOR, SERV_MSG_COLOR)

        elif self.type == 'word game data':
            string = f'%s[GAME] %s[{self.get_send_time()}]%s: %s{self.text}' % \
                     (TYPE_INFO_COLOR, TIME_COLOR, MSG_SMBL_PRE_COLOR, SERV_MSG_COLOR)

        else:
            string = f'%s[NOT FOR PRINT! | type={self.type}] %s[{self.get_send_time()}]%s: %s{self.text}' % \
                     (Fore.LIGHTMAGENTA_EX, TIME_COLOR, MSG_SMBL_PRE_COLOR, SERV_MSG_COLOR)

        try:

            print(string + Style.RESET_ALL)

        except Exception as er:
            print(f'In msg console_print_colored:', er)



