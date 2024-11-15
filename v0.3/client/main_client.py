import sys
from random import randint
from threading import Thread

from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QInputDialog, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QMessageBox

from client_settings import *
from client import Client
from msg import Msg


# from PyQt6.QtWidgets import QMainWindow, QApplication
class AlertDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HELLO!")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel("Something happened, is that OK?")
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class ChatApp(QtWidgets.QMainWindow, Client):

    def __init__(self):
        super().__init__()
        self.nick = f'unnamed{randint(0, 1000)}'
        # self.ask_nick()

        uic.loadUi("main.ui", self)
        self.setWindowTitle('Игра в слова (WordGame)')

        self.send_chat_btn.clicked.connect(self.send_btn_chat_prees)
        self.send_game_btn.clicked.connect(self.send_btn_game_prees)

        self.btnNickEdit.clicked.connect(self.nick_edit)
        self.btnAbout.clicked.connect(self.about)

        # client
        self.connect_to_server()
        self.on_msg = self.procces_msg_as_app
        self.letter_now = '?'

    def about(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("О программе")
        dlg.setText(ABOUT_TEXT)
        button = dlg.exec()



    def update_self_nick_to_server(self):
        self.process_input(f'/nick {self.nick}')

    def nick_edit(self):
        self.ask_nick()

    def ask_nick(self):
        nick, ok_pressed = QInputDialog.getText(self, "Введите ваш никнейм в игре",
                                                "Введите ник")
        if ok_pressed:
            # self.button_1.setText(name)
            self.nick = nick
            self.update_self_nick_to_server()

    def send_btn_chat_prees(self):
        send_text = self.msg_line_chat.text()
        # print(send_text)
        self.process_input(send_text)

    def send_btn_game_prees(self):
        send_text = self.msg_game_line.text()
        # print(send_text)
        self.process_input(f'/word {send_text}')

    def update_label_letter_now(self):
        self.label_letter_now.setText(f'Буква: {self.letter_now}')

    def procces_msg_as_app(self, msg: Msg):

        if msg.is_for_print():
            to_list_add = str(msg)
            if msg.type == 'word game data' or msg.type == 'word info':
                self.game_history.addItem(to_list_add)


            else:
                self.chat_history.addItem(to_list_add)


        else:
            if msg.type == 'users list update':
                try:
                    users = eval(msg.text)

                except Exception as er:
                    print(f'IN int_cl 38stroka err: {er}')
                    return

                self.players_list.clear()
                self.players_list.insertItems(0, users)

            if msg.type == 'letter now update':
                self.letter_now = msg.text

                self.update_label_letter_now()

    def mainloop(self):
        Thread(target=self.mainloop_client).start()




def except_hook(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = ChatApp()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
