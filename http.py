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
    print a, b
    return str(int(a)+int(b))

def entry():
    with open('website/main.html') as fp:
        return fp.read()

def ack_404(conn, addr, res, data):
    return '<html>404</html>'
