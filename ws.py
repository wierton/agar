#!/usr/bin/python
#-*- coding=utf-8 -*-

import base64
from hashlib import sha1
from common import dich_to_str

def ws_handshake(ucon):
    status = "HTTP/1.1 101 Switching Protocols\r\n"
    handshake = "Upgrade:websocket\r\n" + \
            "Connection:Upgrade\r\n" + \
            "Sec-WebSocket-Accept:"
    magic_str = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    ha = sha1(ucon.headers['Sec-WebSocket-Key'] + magic_str)
    key = base64.encodestring(ha.digest())[:-1]
    ucon.raw_send(status + handshake + key + '\r\n\r\n')

def handler(ucon):
    ws_handshake(ucon)
    while 1:
        ucon.raw_recv()
    ucon.alive = False
