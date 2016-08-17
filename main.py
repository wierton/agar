#!/usr/bin/python
#-*- coding=utf-8 -*-

import os, re, sys, thread
from socket import *
import http, ws
import parse

handler_list = [
        (r'^(gamedat)$' , ws.handler,  True),
        (r'^add/(\d+)/(\d+)$' , http.add,  False),
        (r'^$'        , http.entry, False),
        (r'^(.*)$'    , http.handler, False),
        (r'*'         , http.ack_404, False),
        ]

def switch_handler(conn, addr):
    ucon = parse.load(conn, addr)
    while 1:
        ucon.recv()
        suc_match = False
        for tup in handler_list:
            match = re.match(tup[0], ucon.rfile)
            if match:
                suc_match = True
                if not tup[2]:
                    sdata = tup[1](*match.groups())
                    ucon.send(sdata)
                else:
                    tup[1](ucon, *match.groups())
                break
        if not ucon.alive or not suc_match:
            ucon.close()
            break

def parse_args():
    args = ''.join(sys.argv[1:])
    regexs = [
        (r'^(\d+\.\d+\.\d+\.\d+):(\d+)$',
            lambda x:(x.group(1),x.group(2))),
        (r'^(\d+)$',
            lambda x:('127.0.0.1', x.group(1))),
        (r'^(\d+\.\d+\.\d+\.\d+)$',
            lambda x:(x.group(1), '8080'))
        ]
    for regex in regexs:
        result = re.match(regex[0], args)
        if result:
            addr, port = regex[1](result)
            return addr, int(port)
    print 'Invalid IP address or port !!!'
    exit(0)

addr, port = '127.0.0.1', 8080
if len(sys.argv) > 1 :
    addr, port = parse_args()
print addr, port
try:
    s = socket(AF_INET, SOCK_STREAM)
except:
    print 'socket creation fails'
    exit(-1)
try:
    s.bind((addr, port))
    s.listen(10)
    while 1:
        conn,addr = s.accept()
        print 'connected by', addr
        thread.start_new_thread(switch_handler, (conn, addr))
finally:
    s.close()
