#!/usr/bin/python
#-*- coding=utf-8 -*-

import log
import websocket
import math, json, random

cellWidth     = 500
cellHeight    = 500
wholeWidth    = 2000
wholeHeight   = 2000
playerMaxNum  = 20
ballMaxNum    = 320#at most 16 ball for per player
fruitMaxNum   = 200
maxDist       = 100
playerActiveIdArray = []
playerAvailIdArray  = [0] * playerMaxNum
playerWebSocketArray= [0] * playerMaxNum
playerNameArray     = [''] * playerMaxNum
playerLiveArray     = [0] * playerMaxNum
playerPosXArray     = [0.] * playerMaxNum
playerPosYArray     = [0.] * playerMaxNum
playerDirXArray     = [0.] * playerMaxNum
playerDirYArray     = [0.] * playerMaxNum
ballPosXArray       = [0.] * playerMaxNum
ballPosYArray       = [0.] * playerMaxNum
fruitLiveArray      = [0] * fruitMaxNum
fruitPosXArray      = [0.] * fruitMaxNum
fruitPosYArray      = [0.] * fruitMaxNum
playerRadiusArray   = [0.] * playerMaxNum
playerMaxSpeedArray = [0.] * playerMaxNum

def init():
    for i in range(playerMaxNum):
        playerAvailIdArray [i] = i
        playerLiveArray    [i] = True
        playerPosXArray    [i] = random.uniform(0, wholeWidth)
        playerPosYArray    [i] = random.uniform(0, wholeHeight)
        playerDirXArray    [i] = random.random()
        playerDirYArray    [i] = random.random()
        playerRadiusArray  [i] = 20
        playerMaxSpeedArray[i] = 3.0
    for i in range(fruitMaxNum):
        fruitLiveArray     [i] = True
        fruitPosXArray     [i] = random.random() * wholeWidth
        fruitPosYArray     [i] = random.random() * wholeHeight

def getFreePlayerId():
    if len(playerAvailIdArray) > 0:
        availId = playerAvailIdArray.pop()
        playerActiveIdArray.append(availId)
        return availId
    else:
        return -1

def checkCollision(playerId):
    playerX = playerPosXArray[playerId]
    playerY = playerPosYArray[playerId]
    playerR = playerRadiusArray[playerId]
    for i in playerActiveIdArray:
        if i == playerId or not playerLiveArray[i]:
            continue
        x = playerPosXArray[i]
        y = playerPosYArray[i]
        r = playerRadiusArray[i]
        dx = x-playerX
        dy = y-playerY
        dist = math.sqrt(dx*dx+dy*dy)
        if r + 1 < playerR and dist + r < playerR + 1:
            playerR = math.sqrt(r*r+playerR*playerR)
            playerLiveArray[i] = False
            playerWebSocketArray[i].send('{"header":"status", "status":"dead"}')

    for i in range(fruitMaxNum):
        if not fruitLiveArray[i]:
            continue
        x = fruitPosXArray[i]
        y = fruitPosYArray[i]
        r = 5
        dx = x-playerX
        dy = y-playerY
        dist = math.sqrt(dx*dx+dy*dy)
        if r + 1 < playerR and dist + r < playerR:
            playerR = math.sqrt(r*r+playerR*playerR + 1)
            fruitLiveArray[i] = False
    playerRadiusArray[playerId] = playerR

def responseUpdate(obj):
    retJSON = {}
    playerId = int(obj['playerId'])
    width = obj['width']
    height = obj['height']
    playerX = playerPosXArray[playerId]
    playerY = playerPosYArray[playerId]
    playerR = playerRadiusArray[playerId]

    if not playerId in playerActiveIdArray:
        return {"header":"status", "status":"dead"}

    retJSON['player'] = {}
    retJSON['enemy']  = []
    retJSON['fruit']  = []
    for i in playerActiveIdArray:
        x = playerPosXArray[i]
        y = playerPosYArray[i]
        r = playerRadiusArray[i]
        if playerLiveArray[i] \
	and 2*math.fabs(x-playerX) < width \
        and 2*math.fabs(y-playerY) < height:
            retJSON['enemy'].append({"x":x,"y":y,"r":r})

    for i in range(fruitMaxNum):
        x = fruitPosXArray[i]
        y = fruitPosYArray[i]
        if fruitLiveArray[i] \
        and 2*math.fabs(x-playerX) < width \
        and 2*math.fabs(y-playerY) < height:
            retJSON['fruit'].append({"x":x,"y":y})

    if playerLiveArray[playerId]:
        dx = obj['dirX']
        dy = obj['dirY']
        dist = math.sqrt(dx*dx+dy*dy)
        rate = [dist/maxDist, 1][dist > maxDist]
        playerSpeed = rate * playerMaxSpeedArray[playerId]
        
        finalX = playerX + playerSpeed * dx / dist
        finalY = playerY + playerSpeed * dy / dist

        if finalX > 0 and finalX < wholeWidth:
            playerX = playerPosXArray[playerId] = finalX
        if finalY > 0 and finalY < wholeHeight:
            playerY = playerPosYArray[playerId] = finalY
        
        checkCollision(playerId)

    retJSON['player'] = {"x":playerX, "y":playerY, "r":playerR}
    return retJSON

def responseInit(obj):
    retObj = {}
    playerId = int(obj['playerId'])
    if playerId == -1:
        playerId = int(getFreePlayerId())
    else:
        playerLiveArray[playerId] = True
    playerNameArray[playerId] = obj['name']
    playerPosXArray[playerId] = random.uniform(0, wholeWidth)
    playerPosYArray[playerId] = random.uniform(0, wholeHeight)
    retObj['playerId'] = playerId
    retObj['playerRadius'] = playerRadiusArray[playerId]
    retObj['pos'] = {}
    retObj['pos']['x'] = playerPosXArray[playerId]
    retObj['pos']['y'] = playerPosYArray[playerId]
    return retObj

# send and post
def handle_data(dataFromClient):
    data_valid = True
    try:
        obj = json.loads(dataFromClient)
    except:
        data_valid = False
    if not data_valid or not obj.get('header'):
        log.e('ws get invalid data (len={}):{}'.format(len(dataFromClient), ','.join('%x'%(ord(i)) for i in dataFromClient)))
        return {"header":"unknown"}
    switcher = {
            'init':responseInit,
            'update':responseUpdate,
            }
    retObj = switcher[obj['header']](obj)
    if not 'header' in retObj:
        retObj['header'] = obj['header']
    return retObj

def handler(ucon):
    playerId = -1
    ws = websocket.load(ucon)
    while 1:
        ws.recv()
        if ws.closed:
            ucon.alive = False
            break
        obj = handle_data(ws.data)
        ws.send(json.dumps(obj))
        if obj.get('header') == 'init':
            playerId = int(obj['playerId'])
            playerWebSocketArray[playerId] = ws

init()
