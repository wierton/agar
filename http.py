#!/usr/bin/python
#-*- coding=utf-8 -*-

import os

def handler(rfile):
    if rfile == '' or not os.path.exists('website/' + rfile):
        rfile = 'website/404.html'
    else:
        rfile = 'website/' + rfile
    with open(rfile) as fp:
        return fp.read()

def add(a, b):
    return str(int(a)+int(b))

def entry():
    with open('website/main.html') as fp:
        return fp.read()

def res_ip(ucon, addr, port):
    ucon.alive = False
    return '{{"addr":"{0}", "port":"{1}"}}'.format(addr, port)

def ack_404():
    return '<html>404</html>'
