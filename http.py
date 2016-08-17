#!/usr/bin/python
#-*- coding=utf-8 -*-

import os, re, sys, time
from socket import *

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

def make_headers(headers):
    ret = ''
    for index in headers:
        ret += index + ':' + headers[index] + "\r\n"
    ret += "\r\n"
    return ret

def judge_connection(dic):
    if  not dic.get('connection') \
        or 'keep-alive' != dic['connection'].lower():
        return -1
    return 0

def make_response(res, dic):
    status = "HTTP/1.1 200 OK\r\n"
    headers = {
        "Content-Length"   :"0",
        "Content-Type"     :"",
        "Date"             :get_asctime(),
        "Load-Balancing"   :"web06"
        }
    if judge_connection(dic) >= 0:
        headers['Connection'] = 'keep-alive'
    with open(res) as fp:
        body = fp.read()
    headers["Content-Type"] = get_filetype(res)
    headers['Content-Length'] = str(len(body))
    return status + make_headers(headers) + body

def parse_headers(headers):
    ppa = re.compile(r'^\s*(.*?)\s*:\s*(.*?)\s*\r?$', re.M)
    result = ppa.findall(headers)
    dic = {item[0]:item[1] for item in result}
    return dic

def split_data(data):
    res = 'main.html'
    headers, body  = data.split('\r\n\r\n', 1)[0:2]
    proto, headers = headers.split('\n', 1)[0:2]
    pa  = re.compile('(GET|POST)\s+(\S+)\s+HTTP/1.1')
    result = pa.match(proto)
    if result:
        tmp = result.group(2)
        if tmp != '/':
            if tmp[0] != '/':res = tmp
            else            :res = tmp[1:]
    if not os.path.exists(res):
        res = '404.html'
    return res, headers, body

def handler(conn, addr, data):
    while 1:
        res, headers, body = split_data(data)
        dic  = parse_headers(headers)
        response = make_response(res, dic)
        conn.sendall(response)
        if judge_connection(dic) < 0:
            conn.close()
            print 'disconnect with :', addr
            break
        data = conn.recv(64*1024)

def ack_404(conn, addr, res, data):
    pass
