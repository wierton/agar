var cellWidth     = 500;
var cellHeight    = 500;
var wholeWidth    = 2000;
var wholeHeight   = 2000;
var playerMaxNum  = 20;
var ballMaxNum    = 320;//at most 16 ball for per player
var fruitMaxNum   = 200;
var maxDist       = 100;
var playerAvailIdArray  = new Array(playerMaxNum);
var playerLiveArray     = new Array(playerMaxNum);
var playerPosXArray     = new Array(playerMaxNum);
var playerPosYArray     = new Array(playerMaxNum);
var playerDirXArray     = new Array(playerMaxNum);
var playerDirYArray     = new Array(playerMaxNum);
var ballPosXArray       = new Array(playerMaxNum);
var ballPosYArray       = new Array(playerMaxNum);
var fruitLiveArray      = new Array(fruitMaxNum);
var fruitPosXArray      = new Array(fruitMaxNum);
var fruitPosYArray      = new Array(fruitMaxNum);
var playerRadiusArray   = new Array(playerMaxNum);
var playerMaxSpeedArray = new Array(playerMaxNum);

(function(){
	for(var i = 0; i < playerMaxNum; i++)
	{
		playerAvailIdArray [i] = i;
		playerLiveArray    [i] = true;
		playerPosXArray    [i] = Math.random() * wholeWidth;
		playerPosYArray    [i] = Math.random() * wholeHeight;
		playerDirXArray    [i] = Math.random();
		playerDirYArray    [i] = Math.random();
		playerRadiusArray  [i] = 20;
		playerMaxSpeedArray[i] = 3.0;
	}
	for(var i = 0; i < fruitMaxNum; i++)
	{
		fruitLiveArray     [i] = true;
		fruitPosXArray     [i] = Math.random() * wholeWidth;
		fruitPosYArray     [i] = Math.random() * wholeHeight;
	}
})();

function getFreePlayerId()
{
	if(playerAvailIdArray.length > 0)
		return playerAvailIdArray.pop();
	else
		return -1;
}

function responseInit(obj)
{
	var playerId;
	var retObj = {};
	playerId = retObj.playerId = getFreePlayerId();
	retObj.playerRadius = playerRadiusArray[playerId];
	retObj.pos = {};
	retObj.pos.x = playerPosXArray[playerId];
	retObj.pos.y = playerPosYArray[playerId];
	return retObj;
}

function checkCollision(playerId)
{
	var playerX = playerPosXArray[playerId];
	var playerY = playerPosYArray[playerId];
	var playerR = playerRadiusArray[playerId];
	for(var i = 0; i < playerMaxNum; i++)
	{
		if(i == playerId || !playerLiveArray[i])
			continue;
		var x = playerPosXArray[i];
		var y = playerPosYArray[i];
		var r = playerRadiusArray[i];
		var dx = x-playerX;
		var dy = y-playerY;
		var dist = Math.sqrt(dx*dx+dy*dy);
		if(r + 1 < playerR && dist + r < playerR + 1)
		{
			playerR = Math.sqrt(r*r+playerR*playerR);
			playerLiveArray[i] = false;
		}
	}

	for(var i = 0; i < fruitMaxNum; i++)
	{
		if(!fruitLiveArray[i])
			continue;
		var x = fruitPosXArray[i];
		var y = fruitPosYArray[i];
		var r = 5;
		var dx = x-playerX;
		var dy = y-playerY;
		var dist = Math.sqrt(dx*dx+dy*dy);
		if(r + 1 < playerR && dist + r < playerR)
		{
			playerR = Math.sqrt(r*r+playerR*playerR + 1);
			fruitLiveArray[i] = false;
		}
	}
	playerRadiusArray[playerId] = playerR;
}

function responseUpdate(obj)
{
	/* {"header":"update", "body":{}}
	 * update-request {
	 *		"playerId":12,
	 *		"dirX":123,
	 *		"dirY":456,
	 *		"actualWidth":1366,
	 *		"actualHeight":768,
	 *		"zoomRate":1.0	}
	 * update-response {
	 *		"player":{"x":465, "y":789},
	 *		"enemy":{"x":465, "y":789},
	 *		"fruit":{"x":465, "y":789}
	 * }
	 */
	var retJSON = {};
	var playerId = obj.body.playerId;
	var actualWidth = obj.body.actualWidth;
	var actualHeight = obj.body.actualHeight;
	var playerX = playerPosXArray[playerId];
	var playerY = playerPosYArray[playerId];
	var playerR = playerRadiusArray[playerId];

	var dx = obj.body.dirX;
	var dy = obj.body.dirY;
	var dist = Math.sqrt(dx*dx+dy*dy);
	var rate = (dist > maxDist) ? 1 : (dist/maxDist);
	var playerSpeed = rate * playerMaxSpeedArray[playerId];

	var finalX = playerX + playerSpeed * dx / dist;
	var finalY = playerY + playerSpeed * dy / dist;

	retJSON.player = {};
	retJSON.enemy  = [];
	retJSON.fruit  = [];
	checkCollision(playerId);
	for(var i = 0; i < playerMaxNum; i++)
	{
		var x = playerPosXArray[i];
		var y = playerPosYArray[i];
		var r = playerRadiusArray[i];
		if(playerLiveArray[i]
		&& 2*Math.abs(x-playerX) < actualWidth
		&& 2*Math.abs(y-playerY) < actualHeight)
		{
			retJSON.enemy.push({"x":x,"y":y,"r":r});
		}
	}

	for(var i = 0; i < fruitMaxNum; i++)
	{
		var x = fruitPosXArray[i];
		var y = fruitPosYArray[i];
		if(fruitLiveArray[i]
		&& 2*Math.abs(x-playerX) < actualWidth
		&& 2*Math.abs(y-playerY) < actualHeight)
			retJSON.fruit.push({"x":x,"y":y});
	}

	if(finalX > 0 && finalX < wholeWidth)
		playerX = playerPosXArray[playerId] = finalX;
	if(finalY > 0 && finalY < wholeHeight)
		playerY = playerPosYArray[playerId] = finalY;

	retJSON.player = {"x":playerX, "y":playerY, "r":playerR};
	return retJSON;
}

/*send and post*/
function postDataToServer(dataFromClient)
{
	var retObj = {};
	var obj = JSON.parse(dataFromClient);
	switch(obj.header) {
		case 'init':
			retObj = responseInit(obj);
			break;
		case 'update':
			retObj = responseUpdate(obj);
			break;
	}
	return JSON.stringify(retObj);
}
