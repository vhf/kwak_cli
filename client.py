from pprint import pprint
from time import sleep

from MeteorClient import MeteorClient


class Client:
    def __init__(self, username, password, ui):
        self.username = username
        self.password = password
        self.ui = ui
        self.client = MeteorClient('wss://kwak.io/websocket')
        self.client.connect()
        self.client.login(self.username, self.password, callback=self.logged_in)


        self.hot_channels = []
        self.hot_channels_name = []
        self.current_channel = 'main'
        self.client.call('getHotChannels', [], self.set_hot_channels_name)

        self.client.on('connected', self.connected)
        self.client.on('added', self.added)

    def set_hot_channels_name(self, error, result):
        if error:
            self.ui.chatbuffer_add(error)
            return
        self.hot_channels_name = result

    def subscribe_to_channel(self, channel):
        self.current_channel = channel
        try:
            self.client.unsubscribe('messages')
        except:
            pass
        self.ui.chatbuffer_add('* LISTENING TO CHANNEL {}'.format(channel))
        self.client.subscribe('messages', [self.current_channel])

    def subscribe_to_users(self):
        self.client.subscribe('users')

    def added(self, collection, id, fields):
        if collection == 'messages':
            self.ui.chatbuffer_add(fields['text'])
        elif collection == 'users':
            self.ui.userlist.append(fields['username'])
            self.ui.redraw_userlist()

    def connected(self):
        self.ui.chatbuffer_add('* CONNECTED')

    def logged_in(self, error, data):
        if error:
            self.ui.chatbuffer_add('LOGIN ERROR {}'.format(error))
        else:
            self.ui.chatbuffer_add('* LOGGED IN')
