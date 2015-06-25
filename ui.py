import curses

class ChatUI:
    def __init__(self, stdscr, userlist_width=16):
        self.stdscr = stdscr
        self.userlist = []
        self.inputbuffer = ""
        self.linebuffer = []
        self.chatbuffer = []
        self.chanlist = [' ABCDEFGHIJKLMNOPQR ', 'main']

        # Curses, why must you confuse me with your height, width, y, x
        termY, termX = stdscr.getmaxyx()

        # h, w, y, x
        padd_ui = 1
        padd_lt = 2
        self.coordsBox = {
            'channel':  [ termY -2, 18 +padd_lt, 0, 0],
            'user':     [ termY -(2 +3), 18 +padd_lt, 3, termX -(18+2)],
            'chathead': [ 1, termX -(18+padd_lt +padd_ui), 1, 0 +(18+padd_lt) +padd_ui],
            'chatbody': [ termY -((1 +padd_ui)+(1+padd_ui)+padd_ui), termX -((18+padd_lt)+(18+padd_lt)+(padd_ui*2)), 3, (18 +padd_lt) +padd_ui],
            'chatline': [ 1, termX, termY -1, 0]
        }
        coordsBox_channels = ( termY -2, 10, 0, 0        )
        coordsBox_users    = ( termY -2 -3, 10, 2 +1, termX -10)
        coordsBox_chatHead = ( 2, termX -10 -1, 0, 10 +1)
        coordsBox_chatbuffer = ( termY -1 -2 -2, termX -11 -10 -1, 3, 10+1)
        coordsBox_chatline  = ( 1, termX, termY -1, 0)
            
        # define box
        self.box_channels = stdscr.derwin(*self.coordsBox['channel'])
        self.box_users    = stdscr.derwin(*self.coordsBox['user'])
        self.box_chatHead = stdscr.derwin(*self.coordsBox['chathead'])
        self.box_chatbuffer = stdscr.derwin(*self.coordsBox['chatbody'])
        self.box_chatline = stdscr.derwin(*self.coordsBox['chatline'])
        
        self.redraw_ui()

    def resize(self):
        termY, termX = self.stdscr.getmaxyx()
        padd_ui = 1
        padd_lt = 2
        
        # h, w , y, x
        """ Recalcul all boxes """
        # box chathead
        boxChannelSzY, boxChannelSzX = self.box_channels.getmaxyx()
        boxChannelCrY, boxChannelCrX = self.box_channels.getparyx()
        self.coordsBox['chathead'] = [
            self.coordsBox['chathead'][0],
            termX -(boxChannelSzX+padd_ui),
            self.coordsBox['chathead'][2],
            boxChannelSzX +padd_ui
        ]
        """ this 3 lines => for: """
        self.box_chatHead.mvderwin( self.coordsBox['chathead'][2], self.coordsBox['chathead'][3])
        self.box_chatHead.mvwin(    self.coordsBox['chathead'][2], self.coordsBox['chathead'][3])
        self.box_chatHead.resize(   self.coordsBox['chathead'][0], self.coordsBox['chathead'][1])
        # box chatline
        self.coordsBox['chatline'] = [
            self.coordsBox['chatline'][0],
            termX,
            termY -1,
            self.coordsBox['chatline'][3]
        ]
        self.box_chatline.mvderwin( self.coordsBox['chatline'][2], self.coordsBox['chatline'][3])
        self.box_chatline.mvwin(    self.coordsBox['chatline'][2], self.coordsBox['chatline'][3])
        self.box_chatline.resize(   self.coordsBox['chatline'][0], self.coordsBox['chatline'][1])
        # box channel | just h !
        self.coordsBox['channel'][0] = termY -(self.coordsBox['chatline'][0] + padd_ui)
        self.box_channels.mvderwin( self.coordsBox['channel'][2], self.coordsBox['channel'][3])
        self.box_channels.mvwin(    self.coordsBox['channel'][2], self.coordsBox['channel'][3])
        self.box_channels.resize(   self.coordsBox['channel'][0], self.coordsBox['channel'][1])
        
        # box user
        # calcul max size.. actually 18 +padding
        self.coordsBox['user'] = [
            termY -((self.coordsBox['chathead'][2]+self.coordsBox['chathead'][0]+padd_ui)+(self.coordsBox['chatline'][0]+padd_ui)),
            self.coordsBox['user'][1],
            self.coordsBox['chathead'][2] + self.coordsBox['chathead'][0] + padd_ui,
            termX - self.coordsBox['user'][1]
        ]
        self.box_users.mvderwin( self.coordsBox['user'][2], self.coordsBox['user'][3])
        self.box_users.mvwin(    self.coordsBox['user'][2], self.coordsBox['user'][3])
        self.box_users.resize(   self.coordsBox['user'][0], self.coordsBox['user'][1])
        # box chat
        self.coordsBox['chatbody'] = [
            termY -((self.coordsBox['chathead'][2]+self.coordsBox['chathead'][0]+padd_ui)+(self.coordsBox['chatline'][0]+padd_ui)),
            termX - (self.coordsBox['channel'][1] + self.coordsBox['user'][1] + padd_ui + 1),
            self.coordsBox['chathead'][2] + self.coordsBox['chathead'][0] + padd_ui,
            self.coordsBox['channel'][3] + self.coordsBox['channel'][1] + padd_ui
        ]
        self.box_chatbuffer.mvderwin( self.coordsBox['chatbody'][2], self.coordsBox['chatbody'][3])
        self.box_chatbuffer.mvwin(    self.coordsBox['chatbody'][2], self.coordsBox['chatbody'][3])
        self.box_chatbuffer.resize(   self.coordsBox['chatbody'][0], self.coordsBox['chatbody'][1])
        
        # redraw
        self.redraw_ui()
    

    def redraw_ui(self):
        """Redraws the entire UI"""
        termY, termX = self.stdscr.getmaxyx()
        self.stdscr.clear()
        # box chans
        boxSzY, boxSzX = self.box_channels.getmaxyx()
        boxCrY, boxCrX = self.box_channels.getparyx()
        self.stdscr.vline( boxCrY, boxCrX +boxSzX, "|", boxSzY)
        self.chatbuffer_add("COOR_X: " + str(boxCrX))
        self.chatbuffer_add("SIZE_X: " + str(boxSzX))
        # box users
        boxSzY, boxSzX = self.box_users.getmaxyx()
        boxCrY, boxCrX = self.box_users.getparyx()
        self.stdscr.vline( boxCrY, boxCrX -1, "|", boxSzY)
        # box chatHeader
        boxSzY, boxSzX = self.box_chatHead.getmaxyx()
        boxCrY, boxCrX = self.box_chatHead.getparyx()
        self.stdscr.hline(boxCrY -1, boxCrX, "-", boxSzX)
        self.stdscr.hline(boxCrY +boxSzY, boxCrX, "-", boxSzX)
        # box chatbuffer
        boxSzY, boxSzX = self.box_chatbuffer.getmaxyx()
        boxCrY, boxCrX = self.box_chatbuffer.getparyx()
        self.chatbuffer_add("X: " + str(boxSzX))
        #self.stdscr.hline(boxCrY, boxCrX, "A", boxSzX)
        #self.stdscr.hline(boxSzY, boxCrX, "A", boxSzX)
        #self.stdscr.hline(boxCrY +boxSzY, boxCrX, "-", boxSzX)        
        # box message
        boxSzY, boxSzX = self.box_chatline.getmaxyx()
        boxCrY, boxCrX = self.box_chatline.getparyx()
        self.stdscr.hline(boxCrY -1, boxCrX, "-", boxSzX)
        
        self.stdscr.refresh()

        self.redraw_userlist()
        self.redraw_chanlist()
        self.redraw_chathead()
        self.redraw_chatbuffer()
        self.redraw_chatline()

        
        
    '''def resize(self):
        """Handles a change in terminal size"""
        u_h, u_w = self.win_userlist.getmaxyx()
        h, w = self.stdscr.getmaxyx()

        self.win_chatline.mvwin(h - 1, 0)
        self.win_chatline.resize(1, w)

        self.win_userlist.resize(h - 2, u_w)
        self.win_chatbuffer.resize(h - 2, w - u_w - 2)

        self.linebuffer = []
        for msg in self.chatbuffer:
            self._linebuffer_add(msg)

        self.redraw_ui()
        '''

    def redraw_chathead(self):
        """Redraw the userlist"""
        self.box_chatHead.clear()
        h, w = self.box_chatHead.getmaxyx()
        i = 1
        self.box_chatHead.addstr(0, w -2, "#")
        self.box_chatHead.addstr(0, 0, "#SuperKwakChannel")
        self.box_chatHead.refresh()

    
    def redraw_chanlist(self):
        """Redraw the userlist"""
        self.box_channels.clear()
        h, w = self.box_channels.getmaxyx()
        for i, name in enumerate(self.chanlist):
            if i >= h:
                break
            #name = name.ljust(w - 1) + "|"
            self.box_channels.addstr(i, 0, name)
        self.box_channels.addstr(h -1, 0, "MAXCHAN")
        self.box_channels.refresh()

    def redraw_chatline(self):
        """Redraw the user input textbox"""
        h, w = self.box_chatline.getmaxyx()
        self.box_chatline.clear()
        start = len(self.inputbuffer) - w + 1
        if start < 0:
            start = 0
        self.box_chatline.addstr(0, 0, self.inputbuffer[start:])
        self.box_chatline.refresh()

    def redraw_userlist(self):
        """Redraw the userlist"""
        self.box_users.clear()
        h, w = self.box_users.getmaxyx()
        for i, name in enumerate(self.userlist):
            if i >= h:
                break
            self.box_users.addstr(i, 1, "-" +name[:w - 1])
        self.box_users.refresh()
    
    def redraw_chatbuffer(self):
        """Redraw the chat message buffer"""
        self.box_chatbuffer.clear()
        h, w = self.box_chatbuffer.getmaxyx()
        j = len(self.linebuffer) - h
        if j < 0:
            j = 0
        for i in range(min(h, len(self.linebuffer))):
            self.box_chatbuffer.addstr(i, 0, self.linebuffer[j])
            j += 1
        self.box_chatbuffer.refresh()

    def chatbuffer_add(self, msg):
        """

        Add a message to the chat buffer, automatically slicing it to
        fit the width of the buffer

        """
        self.chatbuffer.append(msg)
        self._linebuffer_add(msg)
        self.redraw_chatbuffer()
        self.redraw_chatline()
        self.box_chatline.cursyncup()

    def _linebuffer_add(self, msg):
        h, w = self.stdscr.getmaxyx()
        u_h, u_w = self.box_users.getmaxyx()
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
        self.box_chatline.cursyncup()
        last = -1
        while last != ord('\n'):
            last = self.stdscr.getch()
            if last == ord('\n'):
                tmp = self.inputbuffer
                self.inputbuffer = ""
                self.redraw_chatline()
                self.box_chatline.cursyncup()
                return tmp[len(prompt):]
            elif last == curses.KEY_BACKSPACE or last == 127:
                if len(self.inputbuffer) > len(prompt):
                    self.inputbuffer = self.inputbuffer[:-1]
            elif last == curses.KEY_LEFT or last == curses.KEY_UP or last == curses.KEY_DOWN or last == curses.KEY_RIGHT:                
                self.intputbuffer = "/dbg"
            elif last == curses.KEY_RESIZE:
                self.resize()
            else:
                curses.ungetch(last)
                self.inputbuffer += self.stdscr.get_wch()
            self.redraw_chatline()


