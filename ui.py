import curses

class ChatUI:
    def __init__(self, stdscr, userlist_width=16):
        self.stdscr = stdscr
        self.userlist = []
        self.chanlist = []
        self.inputbuffer = ""
        self.current_channel = None
        self.linebuffer = []
        self.chatbuffer = []

        # Curses, why must you confuse me with your height, width, y, x
        termY, termX = stdscr.getmaxyx()
        self.coordsBox = {
            'channel':  [termY-2,       20,       0,        0],
            'user':     [termY-5,       20,       3, termX-20],
            'chathead': [      1, termX-21,       1,       21],
            'chatbody': [termY-5, termX-42,       3,       21],
            'chatline': [      1,    termX, termY-1,        0]
        }
        # Declaration of containers
        self.boxes =  {}
        for key in self.coordsBox:
            self.boxes[key] = stdscr.derwin(*self.coordsBox[key])
        self.redraw_ui()


    def resize(self):
        padd_ui = 1
        padd_lt = 2
        termY, termX = self.stdscr.getmaxyx()
        # Recalc all boxes and do not forget: h=0,w=1,y=2,x=3
        boxChannelSzY, boxChannelSzX = self.boxes['channel'].getmaxyx()
        boxChannelCrY, boxChannelCrX = self.boxes['channel'].getparyx()
        self.coordsBox['chathead'][1] = termX -(boxChannelSzX+padd_ui)
        self.coordsBox['chathead'][3] = boxChannelSzX +padd_ui
        self.coordsBox['chatline'][1] = termX
        self.coordsBox['chatline'][2] = termY -1
        self.coordsBox['channel'][0] = termY -(self.coordsBox['chatline'][0] +padd_ui)
        self.coordsBox['user'] = [
            termY -((self.coordsBox['chathead'][2]+self.coordsBox['chathead'][0]+padd_ui)
                    +(self.coordsBox['chatline'][0]+padd_ui)),
            self.coordsBox['user'][1],
            self.coordsBox['chathead'][2] + self.coordsBox['chathead'][0] + padd_ui,
            termX - self.coordsBox['user'][1]
        ]
        self.coordsBox['chatbody'] = [
            termY -((self.coordsBox['chathead'][2]+self.coordsBox['chathead'][0]+padd_ui)
                    +(self.coordsBox['chatline'][0]+padd_ui)),
            termX - (self.coordsBox['channel'][1] + self.coordsBox['user'][1] + padd_ui + 1),
            self.coordsBox['chathead'][2] + self.coordsBox['chathead'][0] + padd_ui,
            self.coordsBox['channel'][3] + self.coordsBox['channel'][1] + padd_ui
        ]
        # Apply changes
        for key in self.boxes:
            self.boxes[key].mvderwin( self.coordsBox[key][2], self.coordsBox[key][3])
            self.boxes[key].mvwin(    self.coordsBox[key][2], self.coordsBox[key][3])
            self.boxes[key].resize(   self.coordsBox[key][0], self.coordsBox[key][1])

        """
        self.linebuffer = []
        for msg in self.chatbuffer:
            self._linebuffer_add(msg)
        """
        self.redraw_ui()


    def redraw_ui(self):
        """Redraws the entire UI"""
        termY, termX = self.stdscr.getmaxyx()
        self.stdscr.clear()
        # box chans
        boxSzY, boxSzX = self.boxes['channel'].getmaxyx()
        boxCrY, boxCrX = self.boxes['channel'].getparyx()
        self.stdscr.vline( boxCrY, boxCrX +boxSzX, "|", boxSzY)
        # box users
        boxSzY, boxSzX = self.boxes['user'].getmaxyx()
        boxCrY, boxCrX = self.boxes['user'].getparyx()
        self.stdscr.vline( boxCrY, boxCrX -1, "|", boxSzY)
        # box chatHeader
        boxSzY, boxSzX = self.boxes['chathead'].getmaxyx()
        boxCrY, boxCrX = self.boxes['chathead'].getparyx()
        self.stdscr.hline(boxCrY -1, boxCrX, "-", boxSzX)
        self.stdscr.hline(boxCrY +boxSzY, boxCrX, "-", boxSzX)
        # box chatbuffer
        boxSzY, boxSzX = self.boxes['chatbody'].getmaxyx()
        boxCrY, boxCrX = self.boxes['chatbody'].getparyx()
        # box message
        boxSzY, boxSzX = self.boxes['chatline'].getmaxyx()
        boxCrY, boxCrX = self.boxes['chatline'].getparyx()
        self.stdscr.hline(boxCrY -1, boxCrX, "-", boxSzX)

        self.stdscr.refresh()

        self.redraw_userlist()
        self.redraw_chanlist()
        self.redraw_chathead()
        self.redraw_chatbuffer()
        self.redraw_chatline()

    def redraw_chathead(self, channel=None):
        """Redraw the userlist"""
        self.boxes['chathead'].clear()
        h, w = self.boxes['chathead'].getmaxyx()
        i = 1
        if (channel == None and self.current_channel == None):
            self.boxes['chathead'].addstr(0, 0, "Type \"/join ChannelName\" to start chatting !")
        elif (channel != None):
            self.current_channel = channel
            self.boxes['chathead'].addstr(0, 0, " #" + str(channel))
        else:
            self.boxes['chathead'].addstr(0, 0, " #" + str(self.current_channel))
        self.boxes['chathead'].addstr(0, w -(6 +1), "[HIDE]")
        self.boxes['chathead'].refresh()

    def redraw_chanlist(self):
        """Redraw the userlist"""
        self.boxes['channel'].clear()
        h, w = self.boxes['channel'].getmaxyx()
        for i, name in enumerate(self.chanlist):
            if i >= h:
                break
            self.boxes['channel'].addstr(i, 0, " #" + name)
        self.boxes['channel'].refresh()

    def redraw_chatline(self):
        """Redraw the user input textbox"""
        h, w = self.boxes['chatline'].getmaxyx()
        self.boxes['chatline'].erase()
        start = len(self.inputbuffer) - w + 1
        if start < 0:
            start = 0
        self.boxes['chatline'].addstr(0, 0, self.inputbuffer[start:])
        self.boxes['chatline'].refresh()

    def redraw_userlist(self):
        """Redraw the userlist"""
        self.boxes['user'].clear()
        h, w = self.boxes['user'].getmaxyx()
        for i, name in enumerate(self.userlist):
            if i >= h:
                break
            self.boxes['user'].addstr(i, 1, name[:w - 1])
        self.boxes['user'].refresh()

    def redraw_chatbuffer(self):
        """Redraw the chat message buffer"""
        self.boxes['chatbody'].clear()
        h, w = self.boxes['chatbody'].getmaxyx()
        j = len(self.linebuffer) - h
        if j < 0:
            j = 0
        for i in range(min(h, len(self.linebuffer))):
            self.boxes['chatbody'].addstr(i, 0, self.linebuffer[j])
            j += 1
        self.boxes['chatbody'].refresh()

    def chatbuffer_add(self, msg):
        """

        Add a message to the chat buffer, automatically slicing it to
        fit the width of the buffer

        """
        self.chatbuffer.append(msg)
        self._linebuffer_add(msg)
        self.redraw_chatbuffer()
        self.redraw_chatline()
        self.boxes['chatline'].cursyncup()

    def _linebuffer_add(self, msg):
        h, w = self.stdscr.getmaxyx()
        u_h, u_w = self.boxes['user'].getmaxyx()
        w = w - u_w - 2
        while len(msg) >= w:
            self.linebuffer.append(msg[:w])
            msg = msg[w:]
        if msg:
            self.linebuffer.append(msg)

    def prompt(self, msg):
        """Prompts the user for input and returns it"""
        self.inputbuffer = msg
        self.redraw_chatline()
        res = self.wait_input()
        res = res[len(msg):]
        return res

    def wait_input(self, prompt=""):
        """

        Wait for the user to input a message and hit enter.
        Puts the message into self.inputbuffer

        """
        self.inputbuffer = prompt
        self.redraw_chatline()
        self.boxes['chatline'].cursyncup()
        last = -1
        while last != ord('\n'):
            last = self.stdscr.getch()
            if last == ord('\n'):
                tmp = self.inputbuffer
                self.inputbuffer = ""
                self.redraw_chatline()
                self.boxes['chatline'].cursyncup()
                return tmp[len(prompt):]
            elif last == curses.KEY_BACKSPACE or last == 127:
                if len(self.inputbuffer) > len(prompt):
                    self.inputbuffer = self.inputbuffer[:-1]
            elif last==curses.KEY_LEFT or last==curses.KEY_UP or last==curses.KEY_DOWN or last==curses.KEY_RIGHT:
                self.redraw_ui()
            elif last == curses.KEY_RESIZE:
                self.resize()
            else:
                curses.ungetch(last)
                self.inputbuffer += self.stdscr.get_wch()
            self.redraw_chatline()

    def print_logo(self):
        if (self.coordsBox['chatbody'][1] < 65):
            return 1
        self.chatbuffer_add('                                                               ')
        self.chatbuffer_add('                    .................,,,,,,,,,,,,,,,,,')
        self.chatbuffer_add('                    .................,,,,,,,,,,,,,,,,,')
        self.chatbuffer_add('                    .................,,,,,,,,,,,,,,,,,')
        self.chatbuffer_add('                    .................,,,,,,,,,,,,,,,,,')
        self.chatbuffer_add('                    .................,,,,,,,,,,,,,,,,,')
        self.chatbuffer_add('                ~~~~~~~~~~~~~~~~~~~~:~~~~~~~~~~~~~~~~~')
        self.chatbuffer_add('             ,~~~~~~~~~~~~~~~~~~~~~~:~~~~~~~~~~~~~~~~~')
        self.chatbuffer_add('           :~~~~~~~~~~~~~~~~~~~~~~~~:~~~~~~~~~~~~~~~~~')
        self.chatbuffer_add('          ~~~~~~~~~~~~~~~~~~~~~~~~~~:~~~~~~~~~~~~~~~~~')
        self.chatbuffer_add('        =~~~~~~......................,,,,,,,,,,,,,,,,,,,,,    ')
        self.chatbuffer_add('       ~~~~~~~~......................,,,,,,,,,,,,,,,,,,,,,    ')
        self.chatbuffer_add('      ~~~~~~~~~......................,,,,,,,,,,,,,,,,,,,,,    ')
        self.chatbuffer_add('     ~~~~~~~~~~~~~~~~~+++++++++++++++++++++++++++++,          ')
        self.chatbuffer_add('     ~~~~~~~~~~~~~~~~~++++++++++++++=++++++++++++++,          ')
        self.chatbuffer_add('    ~~~~~~~~~~~~~~~~~~+++++++++++++++++++++,,,,++++,          ')
        self.chatbuffer_add('    ~~~~~~~~~~~~~~~~~~++++++++++++++++++++~,,,,~+++=~~~~~~~~~~')
        self.chatbuffer_add('   ~~~~~~~~~~~~~~~~~~~+++++++++++++++++++++~.,~++++=~~~~~~~~= ')
        self.chatbuffer_add('   ~~~~~~~~~~~~~~~~~~~+++++++++++++++++++++++++++++=~~~~~~~   ')
        self.chatbuffer_add('   ~~~~~~~~~~~~~~~~~~~+++++++++++++++++++++++++++++=~~~~~     ')
        self.chatbuffer_add('   ++++++++++++++++++++++++++++++++++++++++++++++++~~~~~~     ')
        self.chatbuffer_add('   ++++++++++++++++++++++++++++++++++++++++++++++++:~~~~~~    ')
        self.chatbuffer_add('   ++++++++++++++++++++++++++++++++++++++++++++++++:~~~~~~~~  ')
        self.chatbuffer_add('   ++++++++++++++++++++++++++++++++++++++++++++++++~~~~~~~~~~ ')
        self.chatbuffer_add('    +++++++++++++++++++++++++++++++++++++++++++++++           ')
        self.chatbuffer_add('    ++++++++++++++++++++++++++++++++++++++++++++++            ')
        self.chatbuffer_add('     ++++++++++++++++++++++++++++++++++++++++++++             ')
        self.chatbuffer_add('      +++++++++++++++++++++++++++++++++++++++++++             ')
        self.chatbuffer_add('       +++++++++++++++++++++++++++++++++++++++++              ')
        self.chatbuffer_add('        +++++++++++++++++++++++++++++++++++++++               ')
        self.chatbuffer_add('         ++++++++++++++++++++++++++++++++++++                 ')
        self.chatbuffer_add('          ++++++++++++++++++++++++++++++++++                  ')
        self.chatbuffer_add('            ++++++++++++++++++++++++++++++                    ')
        self.chatbuffer_add('               +++++++++++++++++++++++++                      ')
        self.chatbuffer_add('                  +++++++++++++++++++                         ')
        self.chatbuffer_add('                       ++++++++                               ')
        self.chatbuffer_add('                                                              ')
        
