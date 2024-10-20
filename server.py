import datetime
import socket
from threading import Thread
from time import time

from msg import Msg as Msg
from user import *

NICK_ALLOWED_SIMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890_'


class Server:
    def __init__(self):

        # Global variable that mantain client's connections

        self.connections = {}
        self.LISTENING_PORT = 7979
        self.msg_sep = '<SEP>'

    def send(self, client_conn, msg_obj):

        try:
            # Sending message to client connection
            client_conn.send(repr(msg_obj).encode())

        # if it fails, there is a chance of socket has died
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

    def process_message(self, connection, address, msg_content):
        if msg_content.rstrip() == '':
            return
        #print(f'process_message( : {msg_content}')
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

            if self.check_nick(new_nick):

                print(f'user {user.get_nick()} set self nick to {new_nick}')
                self.connections[new_nick] = self.connections[user.get_nick(colored=False)]
                self.connections[new_nick].nick = new_nick
                del self.connections[user.get_nick(colored=False)]

                print(self.connections)

            else:
                self.send(connection, Msg(f'You nick not edited!', None, 'warning'))

        elif msg_.type == 'get users':
            send_text = f'All users: {", ".join(self.get_all_nicks())}'

            self.send(connection, Msg(send_text, None, 'info'))


        elif msg_.type == 'to chat':
            msg_to_send = Msg(f'{msg_text}', nick, 'to chat')

            msg_to_send.console_print_colored()
            self.broadcast(repr(msg_to_send))  # , connection)

    def handle_user_connection(self, connection: socket.socket, address: str):
        user = self.get_user_by_socket(connection)
        msg_summ = ''
        while True:
            try:
                # Get client message
                msg = connection.recv(1024)

                if msg:

                    # s
                    msg_content_str = msg.decode()

                    # slp_sep = msg_content_str.split(self.msg_sep)

                    msg_summ += msg_content_str
                    if msg_summ.endswith(self.msg_sep):
                        # print(f'89: {msg_summ:}')
                        slp_sep_msg_summ = msg_summ.split(self.msg_sep)
                        # print(f'91: {slp_sep_msg_summ:}')
                        for i in slp_sep_msg_summ:
                            self.process_message(connection, address, i)

                        msg_summ = ''
                    # e

                else:
                    self.remove_connection(connection)
                    break
            except ConnectionResetError:

                msg = Msg(f'{user.get_nick()} has disconnected ', None, 'info')
                msg.console_print_colored()
                self.broadcast(repr(msg))  # , connection)
                self.remove_connection(connection)
                break

            except RuntimeError:
                print('RuntimeError')

    def broadcast(self, message, connection=None):
        # print(f'IN BROADCAST: MSG={message}')

        to_remove = []
        for nick, user in self.connections.items():
            # Check if isn't the connection of who's send
            if user.conn != connection:
                try:
                    # Sending message to client connection
                    user.conn.send(message.encode())

                # if it fails, there is a chance of socket has died
                except Exception as e:
                    print(f'Error broadcasting message to {user.conn}: {e} ')

                    to_remove.append(user.conn)

        for i in to_remove:
            self.remove_connection(i)

    def send_all_users(self):
        users = str(self.get_all_nicks())
        msg = Msg(users, None, 'users list update')

        self.broadcast(repr(msg))

    def remove_connection(self, conn: socket.socket):
        if conn in self.get_all_socket_connections():
            conn.close()
            del self.connections[self.get_nick_by_socket(conn)]

        self.send_all_users()

    def add_connection(self, socket_connection, address):

        nick = f'unnamed_{address[0]}_{address[1]}'
        added_user = self.connections[nick] = User(socket_connection, address, nick)

        msg = Msg(f'{added_user.get_nick()} connected!', 'server', 'info')

        msg.console_print_colored()
        self.broadcast(repr(msg))
        self.send_all_users()

    def mainloop(self):
        try:
            # Create server and specifying that it can only handle 4 connections by time!
            socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_instance.bind(('', self.LISTENING_PORT))
            socket_instance.listen(4)

            run_serv_msg = Msg('Server running!', 'server', 'info')
            run_serv_msg.console_print_colored()

            while True:
                socket_connection, address = socket_instance.accept()
                self.add_connection(socket_connection, address)
                Thread(target=self.handle_user_connection, args=[socket_connection, address]).start()

        # except Exception as e:
        #    print(f'An error has occurred when instancing socket: {e}')
        finally:
            # In case of any problem we clean all connections and close the server connection
            if len(self.get_all_socket_connections()) > 0:
                for user in self.connections.values():
                    self.remove_connection(user.conn)

            socket_instance.close()


if __name__ == "__main__":
    serv = Server()
    serv.mainloop()
    input()
