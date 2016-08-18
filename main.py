#!/usr/bin/python
#-*- coding=utf-8 -*-

import log
import os
import re
import sys
import thread
from socket import *
import http
import parse
"""import module you create"""
import back

"""socket, addr, port, conn, regex, ucon"""
handler_list = [
        (r'^(gamedat)$'   , back.handler, ['ucon']),
        (r'^add/(\d+)/(\d+)$' , http.add, ['regex']),
        (r'^get_ip_port$' , http.res_ip , ['ucon', 'addr', 'port']),
        (r'^$'            , http.entry  , []),
        (r'^(.*)$'        , http.handler, ['regex']),
        (r'*'             , http.ack_404, []),
        ]

def switch_handler(s, conn, addr):
    ucon = parse.load(s, conn, addr)
    alternative_args = {
            'socket' : s,
            'addr'   : s.getsockname()[0],
            'port'   : s.getsockname()[1],
            'conn'   : conn,
            'ucon'   : ucon,
            }

    while 1:
        ucon.recv()
        suc_match = False
        for tup in handler_list:
            match = re.match(tup[0], ucon.rfile)
            if match:
                suc_match = True
                args = []
                for key in tup[2]:
                    if key in alternative_args:
                        args.append(alternative_args[key])
                    elif key == 'regex':
                        args += match.groups()
                    else:
                        log.e("Unknown key {}".format(key))
                sdata = tup[1](*args)
                ucon.send(sdata)
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
        log.i("{} {}".format('connected by', addr))
        thread.start_new_thread(switch_handler, (s, conn, addr))
finally:
    s.close()
