#!/usr/bin/python3
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import sys

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
port = int(sys.argv[1])
server = SimpleXMLRPCServer(("localhost", port), requestHandler=RequestHandler) 
server.register_introspection_functions()

bids = []
asks = []
cpos = {}
dpos = {}
fills = []

def register(i):
    global bids, asks, cpos, dpos

    cpos[i] = 0
    dpos[i] = 0
    return 0

def get_info():
    global bids, asks, cpos, dpos, fills

    bids.sort(key=lambda v: v[1], reverse=True)
    asks.sort(key=lambda v: v[1])
    while len(bids) and len(asks) > 0 and bids[0][1] >= asks[0][1]:
        s0, p0, w0 = bids[0]
        s1, p1, w1 = asks[0]
        r = min(s0, s1)
        p = (p0 + p1) / 2
        cpos[w0] += r
        dpos[w0] -= r * p
        cpos[w1] -= r
        dpos[w1] += r * p
        bids[0][0] -= r
        asks[0][0] -= r
        fills.append((r, p, w0, w1))
        if bids[0][0] == 0:
            bids = bids[1:]
        if asks[0][0] == 0:
            asks = asks[1:]
    return (bids, asks, cpos, dpos, fills)

def add_bid(v):
    global bids, asks, cpos, dpos

    bids.append(v)
    return 0

def add_ask(v):
    global bids, asks, cpos, dpos

    asks.append(v)
    return 0

def cancel_bid(i):
    bids.sort(key=lambda v: v[1], reverse=True)
    for bid in bids:
        if bid[2] == i:
            del bid
            return True

def cancel_ask(i):
    asks.sort(key=lambda v: v[1])
    for ask in asks:
        if ask[2] == i:
            del ask
            return True

def cancel_all(i):
    while cancel_bid(i) or cancel_ask(i): ()

server.register_function(register)
server.register_function(get_info)
server.register_function(add_bid)
server.register_function(add_ask)
server.register_function(cancel_bid)
server.register_function(cancel_ask)
server.register_function(cancel_all)

server.serve_forever()

