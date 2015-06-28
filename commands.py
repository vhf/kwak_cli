def dbg(ui, client, rest):
    ui.redraw_userlist()
    ui.chatbuffer_add(str(client.ui.userlist))
    client.client.call('setOnline', [])
    ui.chatbuffer_add(str(ui.boxes))
    
def hot(ui, client, rest):
    ui.chatbuffer_add(', '.join(client.hot_channels_name))
    client.client.call('getHotChannels', [], client.set_hot_channels_name)

def join(ui, client, rest):
    client.subscribe_to_channel(rest)

def lst(ui, client, rest):
    ui.chatbuffer_add(', '.join(client.all_channels_name));
    client.client.call('channelList', [], client.set_all_channels_name)
    ui.redraw_ui()

def quit(ui, client, rest):
    exit(0)

commands = {
    'dbg':  [dbg, 'SYNOPSYS: lala', 'USAGE: lala'],
    'hot':  [hot, 'SYNOPSYS: lala', 'USAGE: lala'],
    'j':    [join, 'SYNOPSYS: lala', 'USAGE: lala'],
    'join': [join, 'SYNOPSYS: lala', 'USAGE: lala'],
    'list': [lst, 'SYNOPSYS: lala', 'USAGE: lala'],
    'quit': [quit, 'SYNOPSYS: lala', 'USAGE: lala'],
}
