#!/usr/bin/python
#-*- coding=utf-8 -*-

import base64
from struct import pack, unpack
from hashlib import sha1
from common import dich_to_str

"""
0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
|                               |Masking-key, if MASK set to 1  |
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------- - - - - - - - - - - - - - - - +
:                     Payload Data continued ...                :
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
|                     Payload Data continued ...                |
+---------------------------------------------------------------+
"""

class WebSocket:
    def __init__(self, conn):
        """connection"""
        self.conn = conn
        """data structure for ws frame"""
        self.fin        = 1
        self.opcode     = 0
        self.payloadlen = 0
        self.mask       = 0
        self.mask_key   = ()
        self.raw_data   = ''
        self.data_st    = 0
        self.data       = ''
    def handshake(self, Sec_WebSocket_Key):
        status = "HTTP/1.1 101 Switching Protocols\r\n"
        handshake = "Upgrade:websocket\r\n" + \
                    "Connection:Upgrade\r\n" + \
                    "Sec-WebSocket-Accept:"
        magic_str = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        ha = sha1(Sec_WebSocket_Key + magic_str)
        key = base64.encodestring(ha.digest())[:-1]
        self.conn.send(status + handshake + key + '\r\n\r\n')
    def parse_data(self):
        fb, sb = unpack("2B", self.raw_data[:2])
        self.opcode = fb & 0x3
        self.fin    = (fb & 0x80) >> 7
        self.mask   = (sb & 0x80) >> 7
        self.payloadlen = sb & 0x7f
        mask_key_st = 2
        print self.payloadlen
        if self.payloadlen == 126:
            self.payloadlen, = unpack(">H", self.raw_data[2:4])
            mask_key_st = 4
        print self.payloadlen
        if self.payloadlen == 127:
            self.payloadlen, = unpack(">L", self.raw_data[2:10])
            mask_key_st = 10
        print self.payloadlen
        if self.mask:
            self.mask_key = unpack("4B", self.raw_data[mask_key_st:mask_key_st+4])
        self.data_st = mask_key_st + 4
        raw_data = self.raw_data[self.data_st:]
        tmp_data = list(unpack(str(len(raw_data))+"B", raw_data))
        for i in range(len(tmp_data)):
            tmp_data[i] ^= self.mask_key[i%4]
        self.data += pack(str(len(tmp_data))+"B", *tmp_data)
        print self.payloadlen, self.data

    def recv(self):
        while not self.fin:
            self.raw_data = self.conn.recv(64*1024)
            self.parse_data()
    def send(self, data):
        pass

def handler(ucon):
    Sec_WebSocket_Key = ucon.headers['Sec-WebSocket-Key']
    ws = WebSocket(ucon.conn)
    ws.handshake(Sec_WebSocket_Key)
    while 1:
        ws.recv()
        ws.send('Hello World!')
    ucon.alive = False
