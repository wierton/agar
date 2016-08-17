#!/usr/bin/python
#-*- coding=utf-8 -*-

import os
import time

def get_asctime():
    tup = time.asctime().split(' ')
    return "%s, %s %s %s %s GMT"%(tup[0],tup[2],tup[1],tup[4],tup[3])

def get_filetype(fname):
    suffix = os.path.splitext(fname)[1][1:].lower()
    dic = { 'html':'text/html',
            'css' :'text/css',
            'js'  :'application/js',
            'json':'application/json',
            'jpg' :'image/jpg',
            'jpeg':'image/jpeg',
            'png' :'image/png',
            'ico' :'image/ico',
            'gif' :'image/gif'
            }
    return ['text/html', dic.get(suffix)][suffix in dic]

def dich_to_str(dich):
    ret = ''
    for index in dich:
        ret += index + ':' + dich[index] + "\r\n"
    ret += "\r\n"
    return ret

def amend_jsfile(addr, port):
    with open('draw.js', 'r+') as fp:
        content = fp.read()
        content = content.replace('ws://127.0.0.1:8080/gamedat', 'ws://' + addr + ':' + port + '/gamedat')
        fp.seek(0, 0)
        fp.write(content)
