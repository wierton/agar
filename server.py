#!/usr/bin/python
#-*- coding=utf-8 -*-

import os, re, sys
from socket import *

default_res_status = "HTTP/1.1 200 OK\n"
default_res_headers = {
        "Connection":"keep-alive",
        "Content-Length":"0",
        "Content-Type":"text/html",
        "Date":"Tue, 02 Aug 2016 20:32:56 GMT",
        "If-Modified-Since":"Sat, 30 Jul 2016 16:00:00 GMT",
        "Load-Balancing":"web06",
        "Load-Balancing":"web06"
        }

def get_filetype(fname):
    suffix = os.path.splitext(fname)[1]
    if 'html' in suffix:return 'text/html'
    elif 'css' in suffix:return 'text/css'
    elif 'js' in suffix:return 'application/js'
    elif 'json' in suffix:return 'application/json'
    elif 'jpg' in suffix:return 'image/jpg'
    elif 'jpeg' in suffix:return 'image/jpeg'
    elif 'png' in suffix:return 'image/png'
    elif 'ico' in suffix:return 'image/ico'
    elif 'gif' in suffix:return 'image/gif'
    return 'text/html'


def make_headers(headers):
    ret = ''
    for index in headers:
        ret += index + ':' + headers[index] + "\n"
    ret += "\r\n"
    return ret

def make_response(status, headers, body):
    headers['Content-Length'] = str(len(body))
    return status + make_headers(headers) + body

def format_request(request):
    req_file = ''
    req_headers = {}
    pa = re.compile('(GET|POST) /(\S*) HTTP/1.1')
    result = pa.match(request)
    if result:
        req_file = result.group(2)
    if req_file == '':
        req_file = 'main.html'
    ppa = re.compile(r'\n(.*?):(.*?)(\r|\n)')
    result = ppa.findall(request)
    for item in result:
        req_headers[item[0]] = item[1]
    return req_file, req_headers

def handle_request(req_file, req_headers):
    print req_file
    if os.path.isdir(req_file):
        return default_res_status, default_res_headers, ''
    if os.path.exists(req_file):
        fp = open(req_file)
        if not fp:
            return default_res_status, default_res_headers, ''
        body = fp.read()
        fp.close()
        default_res_headers["Content-Type"] = get_filetype(req_file)
        return default_res_status, default_res_headers, body
    else:
        return default_res_status, default_res_headers, ''

port = 8080
s = socket(AF_INET, SOCK_STREAM)
if len(sys.argv) > 1:
    port = int(sys.argv[1])
s.bind(('127.0.0.1', port))
s.listen(5)
try:
    while 1:
        conn,addr = s.accept()
        print 'connected by', addr
        while 1:
            data = conn.recv(1024)
            req_file, req_headers = format_request(data)
            res_status, res_headers, res_body = handle_request(req_file, req_headers)
            response = make_response(res_status, res_headers, res_body)
            conn.sendall(response)
finally:
    print 'end\n'
    conn.close()
    s.close()
