#!/usr/bin/python
#-*- coding=utf-8 -*-

import random

cellWidth     = 500
cellHeight    = 500
wholeWidth    = 2000
wholeHeight   = 2000
playerMaxNum  = 20
ballMaxNum    = 320#at most 16 ball for per player
fruitMaxNum   = 200
maxDist       = 100
playerAvailIdArray  = [0.] * playerMaxNum;
playerLiveArray     = [0.] * playerMaxNum;
playerPosXArray     = [0.] * playerMaxNum;
playerPosYArray     = [0.] * playerMaxNum;
playerDirXArray     = [0.] * playerMaxNum;
playerDirYArray     = [0.] * playerMaxNum;
ballPosXArray       = [0.] * playerMaxNum;
ballPosYArray       = [0.] * playerMaxNum;
fruitLiveArray      = [0.] * fruitMaxNum;
fruitPosXArray      = [0.] * fruitMaxNum;
fruitPosYArray      = [0.] * fruitMaxNum;
playerRadiusArray   = [0.] * playerMaxNum;
playerMaxSpeedArray = [0.] * playerMaxNum;

def init():
    for i in range(playerMaxNum):
        playerAvailIdArray [i] = i;
        playerLiveArray    [i] = True;
        playerPosXArray    [i] = random.uniform(0, wholeWidth);
        playerPosYArray    [i] = random.uniform(0, wholeHeight);
        playerDirXArray    [i] = random.random();
        playerDirYArray    [i] = random.random();
        playerRadiusArray  [i] = 20;
        playerMaxSpeedArray[i] = 3.0;
    for i in range(fruitMaxNum):
        fruitLiveArray     [i] = True;
        fruitPosXArray     [i] = random.random() * wholeWidth;
        fruitPosYArray     [i] = random.random() * wholeHeight;

def ack(req_data):
    return 'just'
