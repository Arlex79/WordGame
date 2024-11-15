class User:
    def __init__(self, connection, address, nick):
        self.conn = connection
        self.nick = nick
        self.address = address

        self.color = f'RED))(('

    def get_nick(self, colored=True):
        if colored:
            return f'{self.nick}'

        return self.nick

    def get_address(self, colored=True):
        if colored:
            return f'({self.address[0]}:{self.address[1]})'

        return f'({self.address[0]}:{self.address[1]})'

    def get_nick_and_ip_port(self):
        return f'{self.get_nick()} {self.get_address()}'
