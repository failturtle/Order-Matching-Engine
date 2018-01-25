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
    return (bids, asks, cpos, dpos, fills) 

def add_bid(v):
    global bids, asks, cpos, dpos

    s0, p0, w0 = v
    while s0 > 0 and len(asks) > 0 and p0 >= asks[0][1]:
        s1, p1, w1 = asks[0]
        r = min(s0, s1)
        p = p1
        cpos[w0] += r
        dpos[w0] -= r * p
        cpos[w1] -= r
        dpos[w1] += r * p
        s0 -= r
        asks[0] = (s1 - r, p1, w1)
        fills.append((r, p, w0, w1))
        if asks[0][0] == 0:
            asks = asks[1:]

    if s0 > 0:
        bids.append((s0,p0,w0))
        bids.sort(key=lambda v: v[1], reverse=True)

    return 0

def add_ask(v):
    global bids, asks, cpos, dpos

    s1, p1, w1 = v
    while s1 > 0 and len(bids) > 0 and bids[0][1] >= p1:
        s0, p0, w0 = bids[0]
        r = min(s0, s1)
        p = p0
        cpos[w0] += r
        dpos[w0] -= r * p
        cpos[w1] -= r
        dpos[w1] += r * p
        bids[0] = (s0 - r, p0, w0)
        s1 -= r
        fills.append((r, p, w0, w1))
        if bids[0][0] == 0:
            bids = bids[1:]

    if s1 > 0:
        asks.append((s1,p1,w1))
        asks.sort(key=lambda v: v[1])

    return 0

def cancel_bid(i):
    global bids, asks, cpos, dpos
    for j in range(len(bids)):
        if bids[j][2] == i:
            bids = bids[:j] + bids[j+1:]
            return True
    return False

def cancel_ask(i):
    global bids, asks, cpos, dpos
    for j in range(len(asks)):
        if asks[j][2] == i:
            asks = asks[:j] + asks[j+1:]
            return True
    return False

def cancel_all(i):
    global bids, asks, cpos, dpos
    while cancel_bid(i) or cancel_ask(i): ()
    return 0

server.register_function(register)
server.register_function(get_info)
server.register_function(add_bid)
server.register_function(add_ask)
server.register_function(cancel_bid)
server.register_function(cancel_ask)
server.register_function(cancel_all)

server.serve_forever()

