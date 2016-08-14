#!/usr/bin/python
#-*- coding=utf-8 -*-

import os, re, sys, back, thread
from socket import *

default_res_status = "HTTP/1.1 200 OK\r\n"
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

def make_response(status, headers, body):
    headers['Content-Length'] = str(len(body))
    return status + make_headers(headers) + body

def parse_request(request):
    req_file    = 'main.html'
    req_headers = {}
    req_data    = ''
#   get request file
    pa = re.compile('(GET|POST)\s+(\S+)\s+HTTP/1.1')
    result = pa.match(request)
    if result :
        tmp = result.group(2)
        if tmp != '/':
            if tmp[0] != '/':req_file = tmp
            else            :req_file = tmp[1:]
    else :
        return 'gamedat',{},request
#   split the headers and data
    split_str = request.split('\r\n\r\n', 1)
    split_str.append('')
    request, req_data = split_str[0:2]
#   parse headers
    ppa = re.compile(r'^\s*(.*?)\s*:\s*(.*?)\s*\r?$', re.M)
    result = ppa.findall(request)
    req_headers = {item[0]:item[1] for item in result}
    return req_file, req_headers, req_data

def handle_request(req_file, req_headers, req_data):
    ret_dat = ''
    default_res_headers["Connection"] = 'keep-alive'
    default_res_headers["Content-Type"] = 'text/html'
    if req_file == 'gamedat':
        ret_dat = back.ack(req_data)
    elif os.path.exists(req_file):
        with open(req_file) as fp:
            default_res_headers["Content-Type"] = get_filetype(req_file)
            ret_dat = fp.read()
    else:
        pass
    return default_res_status, default_res_headers, ret_dat

def respond_request(conn, addr):
    while(1):
        data = conn.recv(1024)
        req_file, req_headers, req_data = parse_request(data)
        if req_file == 'gamedat':
            if data == '':continue
            back.ws(conn, addr, req_headers, req_data)
        res_status, res_headers, res_body = handle_request(req_file, req_headers, req_data)
        response = make_response(res_status, res_headers, res_body)
        conn.sendall(response)
        if data == '' \
            or not req_headers.get('Connection') \
            or 'keep-alive' != req_headers['Connection'].lower():
            conn.close()
            print 'disconnect with :', addr
            break;

def amend_jsfile(addr, port):
    with open('draw.js', 'r+') as fp:
        content = fp.read()
        content = content.replace('ws://127.0.0.1:8080/gamedat', 'ws://' + addr + ':' + port + '/gamedat')
        fp.seek(0, 0)
        fp.write(content)

addr = '127.0.0.1'
port = 8080
if len(sys.argv) > 1 :
    port = int(sys.argv[1])
    amend_jsfile(addr, str(port))

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
        print 'connected by', addr
        thread.start_new_thread(respond_request, (conn, addr))
finally:
    s.close()
