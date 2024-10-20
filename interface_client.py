import sys
from threading import Thread
from msg import Msg
from PyQt6 import uic, QtWidgets

from client import Client


# from PyQt6.QtWidgets import QMainWindow, QApplication


class ChatApp(QtWidgets.QMainWindow, Client):

    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.send_chat_btn.clicked.connect(self.send_btn_prees)

        # client
        self.connect_to_server()
        self.on_msg = self.procces_msg_as_app

    def send_btn_prees(self):
        send_text = self.msg_line.text()
        # print(send_text)
        self.process_input(send_text)

    def procces_msg_as_app(self, msg: Msg):
        if msg.is_for_print():
            to_list_add = str(msg)
            self.chat_history.addItem(to_list_add)

        if msg.type == 'users list update':
            try:
                users = eval(msg.text)

            except Exception as er:
                print(f'IN int_cl 38stroka err: {er}')
                return

            self.players_list.clear()
            self.players_list.insertItems(0, users)


    def mainloop(self):
        Thread(target=self.mainloop_client).start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = ChatApp()
    ex.show()
    ex.mainloop()

    exit(app.exec())
