import socket
import threading

from colorama import init, Fore
import csv
from msg import Msg

colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX,
          Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
          Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX,
          Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
          ]

init()


class Client:
    def __init__(self):
        self.server_ip = '127.0.0.1' # default
        self.server_port = 7979           # default
        self.load_server_adress_from_csv()
        self.chat_history_list = []
        self.on_msg = None
        self.msg_sep = '<SEP>'

    def load_server_adress_from_csv(self):


        with open('client_settings.csv', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            data = []
            for index, row in enumerate(reader):
                if index > 10:
                    break
                data.append(row)


            try:
                self.server_ip = data[0][0]
                self.server_port = int(data[0][1])
                #print()

            except Exception as e:
                print(e)


    def connect_to_server(self):
        try:
            # Instantiate socket and start connection with server
            self.socket_instance = socket.socket()
            self.socket_instance.connect((self.server_ip, self.server_port))
            # Create a thread in order to handle messages sent by server
            threading.Thread(target=self.handle_messages).start()

            print(f'Connected to server on {self.server_ip}:{self.server_port}')

        except Exception as e:
            print(f'in __init__ : Error connecting to server socket {e}')
            self.socket_instance.close()

    def procces_server_msg(self, msg: Msg):
        # print(f'recive msg str: {msg}')

        try:
            # self.chat_history_list.append(str(msg))

            if not self.on_msg is None:
                self.on_msg(msg)

            if msg.is_for_print():
                msg.console_print_colored()

        except Exception as ex:

            print(f'print Msg err: ' + repr(ex))

    def procces_serv_text(self, text):
        try:
            if text.rstrip() != '':
                msg_obj = eval(text)
            else:
                return

        except Exception as ex:
            print(f'evaling text err (text={text}): {ex}')
            # print('msg:', text, ' end msg))')
            return

        try:

            self.procces_server_msg(msg_obj)

        except Exception as ex:
            print(ex)
            # print('msg:', text, ' end msg))')

    def handle_messages(self):
        '''
            Receive messages sent by the server and display them to user
        '''
        msg_summ = ''
        while True:
            try:
                curr_msg = self.socket_instance.recv(1024)

                # If there is no message, there is a chance that connection has closed
                # so the connection will be closed and an error will be displayed.
                # If not, it will try to decode message in order to show to user.
                if curr_msg:
                    msg_content_str = curr_msg.decode()

                    # slp_sep = msg_content_str.split(self.msg_sep)

                    msg_summ += msg_content_str
                    if msg_summ.endswith(self.msg_sep):
                        #print(f'89: {msg_summ:}')
                        slp_sep_msg_summ = msg_summ.split(self.msg_sep)
                        #print(f'91: {slp_sep_msg_summ:}')
                        for i in slp_sep_msg_summ:
                            self.procces_serv_text(i)

                        msg_summ = ''




                else:
                    self.socket_instance.close()
                    break

            except Exception as e:
                print(f'Error handling message from server: {e}')
                self.socket_instance.close()
                break

    def send_to_serv(self, data):
        self.socket_instance.send(data.encode())

    def send(self, msg_obj):
        # print(f'send_to_serv_msg_obj( {repr(msg_obj)}')
        self.socket_instance.send(repr(msg_obj).encode())

    def process_input(self, text):
        try:
            if text.rstrip() == '':
                return
            spl = text.split()
            if text == '/quit':
                exit()

            elif spl[0] == '/nick':
                self.send(Msg(f'{spl[1]}', 'server', 'set nick'))

            elif spl[0] == '/help':
                try:
                    self.send(Msg(f'{spl[1]}', 'server', 'help'))
                except IndexError:
                    self.send(Msg(f'all', 'server', 'help'))

            elif spl[0] == '/word':
                try:
                    self.send(Msg(f'{spl[1]}', 'server', 'word'))
                except IndexError:
                    pass


            elif text == '/users':
                self.send(Msg(f'', 'server', 'get users'))

            elif spl[0] == '/w' or spl[0] == '/msg':
                self.send(Msg(f'', 'server', 'get users'))

            else:
                self.send(Msg(f'{text}', 'server', 'to chat'))
        except Exception as e:
            print(f'Error in 151: {e}')
    def mainloop_client(self):
        '''
            Main process that start client connection to the server
            and handle it's input messages
        '''

        try:
            while True:
                msg = input().rstrip()
                if msg != '':
                    self.process_input(msg)

            self.socket_instance.close()

        except Exception as e:
            print(f'Error connecting to server socket {e}')
            self.socket_instance.close()

        finally:
            self.socket_instance.close()


if __name__ == "__main__":
    client = Client()
    client.connect_to_server()
    client.mainloop_client()
