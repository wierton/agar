#!/usr/bin/python
#-*- coding=utf-8 -*-

import log
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
        self.fin      = 0
        self.opcode   = 0
        self.data     = ''
        self.raw_data = ''
        self.closed   = False
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
        if len(self.raw_data) < 2:
            log.e('error happened while recving data(ws)')
            exit(2)
        fb, sb = unpack("2B", self.raw_data[:2])
        self.fin    = (fb & 0x80) >> 7
        self.opcode = fb & 0xf
        mask   = (sb & 0x80) >> 7
        mask_key   = '\0\0\0\0'
        payloadlen = sb & 0x7f
        mask_key_st  = 2
        real_data_st = 0
        if payloadlen == 126:
            payloadlen, = unpack(">H", self.raw_data[2:4])
            mask_key_st = 4
        if payloadlen == 127:
            payloadlen, = unpack(">L", self.raw_data[2:10])
            mask_key_st = 10
        real_data_st = mask_key_st
        if mask:
            mask_key = self.raw_data[mask_key_st:mask_key_st+4]
            real_data_st = mask_key_st+4
        i = 0
        for c in self.raw_data[real_data_st:]:
            self.data += chr(ord(c) ^ ord(mask_key[i]))
            i = (i+1)%4
    def recv(self):
        if self.closed:
            return
        while 1:
            self.fin  = 0
            self.data = ''
            while not self.fin:
                self.raw_data = self.conn.recv(64*1024)
                self.parse_data()
            if self.opcode == 0x8:
                self.closed = True
                break
            elif self.opcode == 0x9:
                print 'PingPong'
                self.raw_data[0] = self.raw_data[0]&0xf0|0xa
                self.conn.send(self.raw_data)
            else:
                break
    def send(self, data):
        if self.closed:
            return
        size  = len(data)
        sdata = ''
        if size < 126:
            sdata += chr(0x81) + chr(size)
        elif size < 65536:
            sdata += chr(0x81) + chr(126) + pack(">H", size)
        else:
            sdata += chr(0x81) + chr(127) + pack(">L", size)
        sdata += data
        self.conn.send(sdata)
    def close(self, status_code=1000):
        data = chr(0x88) + chr(2) + chr(0x8d) + chr(0x3)
        self.conn.send(data)

def handler(ucon):
    Sec_WebSocket_Key = ucon.headers['Sec-WebSocket-Key']
    ws = WebSocket(ucon.conn)
    ws.handshake(Sec_WebSocket_Key)
    while 1:
        ws.recv()
        ws.send('See You lala!'*18)
    ws.close()
    ucon.alive = False
    return ''

def load(ucon):
    Sec_WebSocket_Key = ucon.headers['Sec-WebSocket-Key']
    ws = WebSocket(ucon.conn)
    ws.handshake(Sec_WebSocket_Key)
    return ws
