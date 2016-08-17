#!/usr/bin/python
#-*- coding=utf-8 -*-

import os, re, sys, thread
from socket import *
import http, ws

handler_list = [
        (r'^gamedat$' , ws.handler), 
        (r'^(.*)$'  , http.handler),
        (r'^$'        , http.ack_404),
        ]

def switch_handler(conn, addr):
    req_file = 'main.html'
    data     = conn.recv(64 * 1024)
    proto    = data.split('\n', 1)[0]
    pa = re.compile('(GET|POST)\s+(\S+)\s+HTTP/1.1')
    result = pa.match(proto)
    if result:
        tmp = result.group(2)
        if tmp != '/':
            if tmp[0] != '/':req_file = tmp
            else            :req_file = tmp[1:]
        else:
            pass # req_file == 'main.html'
        for regex in handler_list:
            ma_obj = re.match(regex[0], req_file)
            if ma_obj:
                regex[1](conn, addr, req_file, data)
                return
        conn.close()

def amend_jsfile(addr, port):
    with open('draw.js', 'r+') as fp:
        content = fp.read()
        content = content.replace('ws://127.0.0.1:8080/gamedat', 'ws://' + addr + ':' + port + '/gamedat')
        fp.seek(0, 0)
        fp.write(content)

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
    amend_jsfile(addr, str(port))
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
