#!/usr/bin/python
#-*- coding=utf-8 -*-

import re
import log
import socket
import json
from common import get_asctime, get_filetype, dich_to_str

class Parse:
    def __init__(self, s, conn, addr):
        self.s       = s
        self.conn    = conn
        self.addr    = addr
        self.alive   = True
        """data structure for recv"""
        self.method  = ''
        self.rfile   = ''
        self.params  = []
        self.headers = {}
        self.body    = ''
        self.data    = ''
        """data structure for send"""

    def raw_recv(self):
        self.data = self.conn.recv(64 * 1024)

    def recv(self):
        self.raw_recv()
        if not '\r\n\r\n' in self.data:
            log.e('Unable to parse the data.')
            self.alive = False
            return
        proto_headers, self.body = self.data.split('\r\n\r\n', 1)
        proto, headers = proto_headers.split('\r\n', 1)
        result = re.match(r'(GET|POST)\s+(\S+)\s+HTTP/1.1', proto)
        if not result:
            log.e('unsupported protocol')
            exit(1)
        self.method, res = result.groups()
        if res[0] == '/':
            res = res[1:]
        lis = res.split('?')
        lis.append('')
        self.rfile, query_string = lis[0:2]
        self.params = [tuple((param+'=').split('=')[0:2])
                for param in query_string.split('&')]

        ma_headers = re.findall(r'^\s*(.*?)\s*:\s*(.*?)\s*\r?$', headers, re.M)
        self.headers = {item[0]:item[1] for item in ma_headers}

        #log.d("rfile : {}\nparams : {}\nheaders : {}\nbody : {}".format(self.rfile,  str(self.params), str(self.headers), self.body))

        if not self.headers.get('connection') \
            or 'keep-alive' != self.headers['connection'].lower():
                self.alive = False

    def raw_recv_json(self):
        self.raw_recv()
        return json.loads(self.data)

    def send(self, data='', headers={}):
        status   = "HTTP/1.1 200 OK\r\n"
        sheaders = {
                "Content-Length"   :str(len(data)),
                "Content-Type"     :get_filetype(self.rfile),
                "Date"             :get_asctime(),
                "Load-Balancing"   :"web06"
                }
        headers = dict(sheaders, **headers)
        self.conn.sendall(status + dich_to_str(headers) + data)

    def raw_send(self, data):
        self.conn.sendall(data)

    def raw_send_json(self, dic):
        self.conn.sendall(json.dumps(dic))

    def close(self):
        self.conn.close()
        log.i('Disconnect with:' + str(self.addr))

def load(s, conn, addr):
    parse = Parse(s, conn, addr)
    return parse
