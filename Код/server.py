import datetime
import socket
from threading import Thread
from time import time
from msg import Msg as Msg
from user import *
from time import sleep
import pymorphy2
from string import ascii_letters, digits
import sqlite3

NICK_ALLOWED_SIMBOLS = ascii_letters + digits + '_'


class Server:
    def __init__(self):
        self.connections = {}
        self.LISTENING_PORT = 7900
        self.msg_sep = '<SEP>'
        self.letter_now = 'а'
        self.words_used = []
        self.words_used_with_player = []

    def send(self, client_conn, msg_obj):
        try:
            client_conn.send(repr(msg_obj).encode())

        except Exception as e:
            print(f'Error send message: {e}')
            self.remove_connection(client_conn)

    def log(self, text):
        print(text)

    def check_nick(self, new_nick):
        if len(new_nick) > 16 or len(new_nick) < 3:
            return False

        for i in new_nick:
            if i not in NICK_ALLOWED_SIMBOLS:
                return False

        if new_nick in self.get_all_nicks():
            return False

        return True

    def get_time_now(self):
        return time()

    def get_time_mark(self):
        dt = datetime.datetime.now()
        return dt.strftime('%m.%d.%Y %H:%M:%S')

    def get_nick_by_socket(self, conn):
        for nick, user in self.connections.items():
            if user.conn == conn:
                return user.nick

    def get_user_by_socket(self, conn):
        for nick, user in self.connections.items():
            if user.conn == conn:
                return user

    def get_all_nicks(self):
        all_users = []
        for nick, user in self.connections.items():
            all_users.append(user.get_nick())
        return all_users

    def get_all_socket_connections(self):
        all_users = []
        for nick, user in self.connections.items():
            all_users.append(user.conn)

        return all_users

    def process_message(self, connection, msg_content):
        if msg_content.rstrip() == '':
            return
        try:
            msg_ = eval(msg_content)

        except Exception as e:
            print(f'IN P_M: {e}')
            return

        except SyntaxError:
            print('SyntaxError in process_message')

        user = self.get_user_by_socket(connection)
        nick = user.get_nick()
        msg_text = msg_.text
        if msg_.type == 'set nick':
            new_nick = msg_.text
            try:
                if self.check_nick(new_nick):
                    self.connections[new_nick] = self.connections[user.get_nick(colored=False)]
                    self.connections[new_nick].nick = new_nick
                    del self.connections[nick]
                    self.send(connection, Msg(f'Ваш ник: {new_nick}', None, 'warning'))
                    self.send_all_users_list()
                else:
                    self.send(connection, Msg(f'Ошибка изменения вашего ника!', None, 'warning'))

            except Exception as e:
                print(f'NICK set error: {e}')

        elif msg_.type == 'get users':
            send_text = f'Список игроков: {", ".join(self.get_all_nicks())}'

            self.send(connection, Msg(send_text, None, 'info'))


        elif msg_.type == 'to chat':
            msg_to_send = Msg(f'{msg_text}', nick, 'to chat')

            msg_to_send.console_print_colored()
            self.broadcast(repr(msg_to_send))

        elif msg_.type == 'help':
            if msg_.text == 'nick':
                self.send(connection, Msg('Используйте /nick <новый ник>, для изменения '
                                          'вашего никнейма на <новый ник>', None, 'info'))

            if msg_.text == 'users':
                self.send(connection, Msg('Используйте /users, для отабражения всех учасников игры', None, 'info'))


            else:
                self.send(connection, Msg('Доступные команды: /nick <nick>; /users', None, 'info'))
                self.send(connection, Msg('Для получения дополнительной информации о команде '
                                          'введите /help <имя команды>',
                                          None, 'info'))

        elif msg_.type == 'word':
            self.handle_user_word(msg_.text, user)

    def is_valid_word(self, word):
        morph = pymorphy2.MorphAnalyzer()
        parsed_word = morph.parse(word)[0]
        pos = parsed_word.tag.POS
        number = parsed_word.tag.number
        case = parsed_word.tag.case

        if pos == 'NOUN' and number == 'sing' and (case == 'nomn' or case == 'accs'):
            return True
        return False

    def is_not_already_spoken(self, word):
        if word.lower() not in self.words_used:
            return True

        else:
            return False

    def write_speaked_word_to_db(self, word, nick):
        try:
            con = sqlite3.connect("used_words.sqlite")
            cur = con.cursor()
            cur.execute(f"""INSERT INTO words (word) VALUES ('{word}');""").fetchall()
            con.commit()
            cur.close()

        except Exception as er:
            print(f'Err SQL: {er}')

    def add_word_to_speaked(self, word, nick):
        word = word.lower()
        self.words_used.append(word.lower())
        self.words_used_with_player.append([word, nick])
        self.write_speaked_word_to_db(word, nick)

    def update_now_letter_all_players(self):
        m = Msg(f'{self.letter_now}', None, 'letter now update')
        self.broadcast(repr(m))

    def send_new_word(self):
        new_word = self.words_used_with_player[-1][0]
        new_nick = self.words_used_with_player[-1][1]
        m = Msg(f'\\"{new_word}\\" Теперь подходят слова на букву: \\"{self.letter_now}\\"',
                f'{new_nick}', 'word game data')
        self.broadcast(repr(m))
        self.update_now_letter_all_players()

    def set_now_letter_from_word_and_send_this_info_all(self, word):
        end_letter = word[-1].lower()
        pre_end_letter = word[-2].lower()
        if end_letter == 'й' or end_letter == 'ь':
            self.letter_now = pre_end_letter

        else:
            self.letter_now = end_letter

    def is_word_startswith_letter_now(self, word):
        word = word.lower()
        if word.startswith(self.letter_now):
            return True
        return False

    def handle_user_word(self, word, user):
        nick = user.get_nick()
        conn = user.conn
        word = word.lower()
        if self.is_word_startswith_letter_now(word):
            if self.is_not_already_spoken(word):
                if self.is_valid_word(word):

                    print(f'Новое слово: "{word}"')
                    self.add_word_to_speaked(word, nick)
                    self.set_now_letter_from_word_and_send_this_info_all(word)
                    self.send_new_word()
                    return True

                else:
                    m = Msg(f'Слово "{word}" не найдено!', 'server', 'word game data')
                    self.send(conn, m)
                    return

            else:
                m = Msg(f'Слово "{word}" уже использовано!', 'server', 'word game data')
                self.send(conn, m)
        else:
            m = Msg(f'Слово \\"{word}\\" не начинаеться на \\"{self.letter_now}\\"', 'server', 'word game data')
            self.send(conn, m)
            return

    def handle_user_connection(self, connection: socket.socket, address: str):
        user = self.get_user_by_socket(connection)
        msg_summ = ''
        while True:
            try:
                msg = connection.recv(1024)
                if msg:
                    msg_content_str = msg.decode()
                    msg_summ += msg_content_str
                    if msg_summ.endswith(self.msg_sep):
                        slp_sep_msg_summ = msg_summ.split(self.msg_sep)
                        for i in slp_sep_msg_summ:
                            self.process_message(connection, i)
                        msg_summ = ''
                else:
                    self.remove_connection(connection)
                    break
            except ConnectionResetError:
                msg = Msg(f'{user.get_nick()} вышел из игры...', None, 'info')
                msg.console_print_colored()
                self.broadcast(repr(msg))  # , connection)
                self.remove_connection(connection)
                break
            except RuntimeError:
                print('RuntimeError')
            except OSError as er:
                print(f'OSError___: {er}')
                return
            except Exception as er:
                print(f'Error: {er}')

    def broadcast(self, message, connection=None):
        to_remove = []
        for nick, user in self.connections.items():
            if user.conn != connection:
                try:
                    user.conn.send(message.encode())
                except Exception as e:
                    to_remove.append(user.conn)
        for i in to_remove:
            self.remove_connection(i)

    def send_all_users_list(self):
        users = str(self.get_all_nicks())
        msg = Msg(users, None, 'users list update')
        self.broadcast(repr(msg))

    def remove_connection(self, conn: socket.socket):
        if conn in self.get_all_socket_connections():
            conn.close()
            del self.connections[self.get_nick_by_socket(conn)]
        self.send_all_users_list()

    def add_connection(self, socket_connection, address):
        nick = f'player{len(self.connections) + 1}'
        self.connections[nick] = User(socket_connection, address, nick)
        sleep(0.5)
        nick_set_by_player = self.get_nick_by_socket(socket_connection)
        msg = Msg(f'{nick_set_by_player} присоеденился!', 'server', 'info')
        self.broadcast(repr(msg))
        self.send_all_users_list()

    def mainloop(self):
        try:
            socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_instance.bind(('', self.LISTENING_PORT))
            socket_instance.listen(4)
            run_serv_msg = Msg('Server running!', 'server', 'info')
            run_serv_msg.console_print_colored()
            while True:
                socket_connection, address = socket_instance.accept()
                self.add_connection(socket_connection, address)
                Thread(target=self.handle_user_connection, args=[socket_connection, address]).start()
                self.update_now_letter_all_players()
        finally:

            if len(self.get_all_socket_connections()) > 0:
                for user in self.connections.values():
                    self.remove_connection(user.conn)

            socket_instance.close()


if __name__ == "__main__":
    serv = Server()
    serv.mainloop()
    input()
