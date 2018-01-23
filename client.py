#!/usr/bin/python3
import tkinter as tk
import xmlrpc.client
import sys
import re
import random
import string

n = 30
th = 15
tw = 250

class Application(tk.Frame):
    def __init__(self, master=None):
        server = sys.argv[1]
        port = sys.argv[2]
        my_id = str(random.randint(1,10**10))
        if len(sys.argv) > 3:
            my_id = sys.argv[3]

        self.c = xmlrpc.client.ServerProxy('http://%s:%s' % (server,port))
        self.i = my_id
        self.c.register(self.i)
        self.fp = 0

        super().__init__(master)
        self.pack()
        self['bg'] = 'black'
        self.create_widgets()

    def create_widgets(self):
        self.cf = tk.Frame(self, bg='black')
        self.cf.pack(side='top')

        self.bids = tk.Canvas(self.cf, width=tw, height=th*n, bg='black')
        self.bids.pack(side='left')
        self.bidboxes = []
        for i in range(n):
            self.bidboxes.append(self.bids.create_text(tw-8, (i+1) * th, anchor=tk.SE))

        self.asks = tk.Canvas(self.cf, width=tw, height=th*n, bg='black')
        self.asks.pack(side='right')
        self.askboxes = []
        for i in range(n):
            self.askboxes.append(self.asks.create_text(8, (i+1) * th, anchor=tk.SW))

        self.dx = tk.StringVar()
        self.cash = tk.Entry(self, state=tk.DISABLED, textvariable=self.dx, bg='black')
        self.cash.pack(side='bottom')

        self.cx = tk.StringVar()
        self.con = tk.Entry(self, state=tk.DISABLED, textvariable=self.cx, bg='black')
        self.con.pack(side='bottom')

        self.x = tk.StringVar()
        self.cmd = tk.Entry(self, textvariable=self.x)
        self.cmd.bind('<Key-Return>', self.exec_cmd)
        self.cmd.pack(side='bottom')

        self.refresh()

    def refresh(self):
        obids, oasks, cpos, dpos, fills = self.c.get_info()

        while self.fp < len(fills):
            s, p, wb, ws = fills[self.fp]
            self.fp += 1
            if wb == self.i and ws == self.i:
                print("Did you just fill yourself? wtf calling the SEC")
            elif wb == self.i:
                print("Fill Bid\t%4d\t%2.2f" % (s, p))
            elif ws == self.i:
                print("Fill Ask\t%4d\t%2.2f" % (s, p))

        self.cx.set("Cash:\t    %4.2f" % dpos[self.i])
        self.dx.set("Contracts:\t  %7d" % cpos[self.i])

        cs = 0
        for i in range(n):
            if i < len(obids):
                s,p,w = obids[i]
                cs += s
                fill = 'green' if w == self.i else 'white'
                self.bids.itemconfigure(self.bidboxes[i], text="%4d\t%4d\t%2.1f" % (cs, s, p), fill=fill)
            else:
                self.bids.itemconfigure(self.bidboxes[i], text="")
        cs = 0
        for i in range(n):
            if i < len(oasks):
                s,p,w = oasks[i]
                cs += s
                fill = 'green' if w == self.i else 'white'
                self.asks.itemconfigure(self.askboxes[i], text="%2.1f\t%4d\t%4d" % (p, s, cs), fill=fill)
            else:
                self.asks.itemconfigure(self.askboxes[i], text="")

    def exec_cmd(self, event):
        cmd = self.x.get().lower()
        m = re.match(r'(b|s)\s+(\d+)\s+(\d+(\.\d*)?)$', cmd)
        succ = False
        if m:
            dr = m.group(1)
            s = m.group(2)
            p = m.group(3)
            s = int(s)
            p = float(p)
            p = int(p*10) / 10.
            if s > 0:
                if dr == 'b':
                    self.c.add_bid((s, p, self.i))
                    print("New Order Bid\t%4d\t%2.2f" % (s, p))
                    succ = True
                else:
                    self.c.add_ask((s, p, self.i))
                    print("New Order Ask\t%4d\t%2.2f" % (s, p))
                    succ = True
        if cmd == 'cb':
            self.c.cancel_bid(self.i)
            succ = True
        elif cmd == 'cs':
            self.c.cancel_ask(self.i)
            succ = True
        elif cmd == 'cc':
            self.c.cancel_all(self.i)
            succ = True

        if succ:
            self.refresh()
        else:
            print("You've cooked it m8")

root = tk.Tk()
app = Application(master=root)
app.mainloop()
