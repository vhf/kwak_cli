from curses import wrapper
from ui import ChatUI
from client import Client
import configparser
import time

def main(stdscr):
    cp = configparser.ConfigParser()
    cp.read('config.cfg')
    username = cp.get('credentials', 'username')
    password = cp.get('credentials', 'password').encode('utf-8')

    stdscr.clear()
    ui = ChatUI(stdscr)

    client = Client(username, password, ui)
    client.subscribe_to_channel('dev')
    client.subscribe_to_users('dev')

    message = ''
    while message != '/quit':
        message = ui.wait_input()
        if message[0:6] == '/join ':
            client.subscribe_to_channel(message[6:])
        elif message[0:4] == '/hot':
            ui.chatbuffer_add(', '.join(client.hot_channels_name))
            client.client.call('getHotChannels', [], client.set_hot_channels_name)
        elif message[0:4] == '/dbg':
                client.ui.redraw_userlist()
                client.ui.chatbuffer_add(str(client.ui.userlist))
        elif message != '/quit':
            client.client.insert('messages', {'channel': client.current_channel, 'text': message})

    client.logout()
    time.sleep(3)
wrapper(main)
