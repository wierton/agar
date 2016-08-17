#!/usr/bin/python
#-*- coding=utf-8 -*-


def handler(ucon, rfile):
    print ucon.data
    print ucon.rfile, ucon.params, ucon.headers, ucon.body
    ucon.raw_recv()
    print ucon.data
    ucon.alive = False
    pass
