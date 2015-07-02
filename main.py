from curses import wrapper
from ui import ChatUI
from client import Client
import configparser
import time
from commands import *


def main(stdscr):
    cp = configparser.ConfigParser()
    cp.read('config.cfg')
    username = cp.get('credentials', 'username')
    password = cp.get('credentials', 'password').encode('utf-8')

    stdscr.clear()
    ui = ChatUI(stdscr)

    client = Client(username, password, ui)
    client.subscribe_to_channel(client.current_channel)
    client.subscribe_to_users(client.current_channel)
    
    message = ''
    while message != '/quit':
        try:
            message = ui.wait_input().strip()
            if message != "" and (message[0] != '/' or message[0:2] == '//'):
                client.client.insert('messages', {'channel': client.current_channel, 'text': message})
            else:
                try:
                    end = message.index(' ')
                    command = message[1:end].strip()
                    rest = message[end:].strip()
                except ValueError:
                    command = message[1:].strip()
                    rest = None

                if commands.get(command, False):
                    commands[command][0](ui, client, rest)
                else:
                    ui.chatbuffer_add('Unknown command {}'.format(command))
     
        except KeyboardInterrupt:
            client.logout()
            time.sleep(1)

wrapper(main)

# Could not subscribe because a connection has not been etablished
