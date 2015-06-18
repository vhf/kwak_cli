from curses import wrapper
from ui import ChatUI
from client import Client
import ConfigParser

def main(stdscr):
    cp = ConfigParser.ConfigParser()
    cp.read('config.cfg')
    username = cp.get('credentials', 'username')
    password = cp.get('credentials', 'password')

    stdscr.clear()
    ui = ChatUI(stdscr)

    client = Client(username, password, ui)
    client.subscribe_to_channel('main')
    client.subscribe_to_users()

    message = ''
    while message != '/quit':
        message = ui.wait_input()
        if message[0:6] == '/join ':
            client.subscribe_to_channel(message[6:])
        else:
            client.client.insert('messages', {'channel': client.current_channel, 'text': message})
            ui.chatbuffer_add(message)

wrapper(main)
