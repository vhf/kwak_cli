from pprint import pprint
from time import sleep, mktime
from datetime import datetime

from MeteorClient import MeteorClient


class Client:
    def __init__(self, username, password, ui):
        self.username = username
        self.password = password
        self.ui = ui
        self.now = mktime(datetime.now().timetuple())*1e3
        self.resume_token = ''
        self.client = MeteorClient('wss://kwak.io/websocket')
        self.client.connect()
        self.client.login(self.username, self.password,
            token=self.resume_token, callback=self.logged_in)

        self.hot_channels = []
        self.hot_channels_name = []
        self.current_channel = 'dev'
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

    def subscribe_to_users(self, channel):
        self.client.subscribe('users', [channel])

    def added(self, collection, id, fields):
        # only add new messages, not backlog
        if collection == 'messages' and fields['time'] > self.now:
            # fields : channel | time | text | user
            self.ui.chatbuffer_add('{}\t{}: {}'.format(fields['time'], fields['user'], fields['text']))
        elif collection == 'users':
            # fields : username | profile | color
            if len(fields['profile']) > 0 and bool(fields['profile']['online']) == True:
                self.ui.userlist.append(fields['username'])
                self.ui.redraw_userlist()
            

    def connected(self):
        self.ui.chatbuffer_add('* CONNECTED')

    def logged_in(self, error, data):
        if error:
            self.ui.chatbuffer_add('LOGIN ERROR {}'.format(error))
        else:
            self.resume_token = data['token']
            self.ui.chatbuffer_add('* LOGGED IN')

    def logout(self):
        self.ui.chatbuffer_add('* BYE (LOVELY DUCK)')
