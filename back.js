var cellWidth   = 500;
var cellHeight  = 500;
var wholeWidth    = 2000;
var wholeHeight   = 2000;
var playerMaxNum  = 50;
var fruitMaxNum   = 1000;
var maxDist       = 350;
var playerAvailId       = new Array(playerMaxNum);
var playerPosXArray     = new Array(playerMaxNum);
var playerPosYArray     = new Array(playerMaxNum);
var playerDirXArray     = new Array(playerMaxNum);
var playerDirYArray     = new Array(playerMaxNum);
var fruitPosXArray      = new Array(fruitMaxNum);
var fruitPosYArray      = new Array(fruitMaxNum);
var playerRadiusArray   = new Array(playerMaxNum);
var playerMaxSpeedArray = new Array(playerMaxNum);

(function(){
	for(var i = 0; i < playerMaxNum; i++)
	{
		playerAvailId      [i] = i;
		playerPosXArray    [i] = Math.random() * wholeWidth;
		playerPosYArray    [i] = Math.random() * wholeHeight;
		playerDirXArray    [i] = Math.random();
		playerDirYArray    [i] = Math.random();
		fruitPosXArray     [i] = Math.random() * wholeWidth;
		fruitPosXArray     [i] = Math.random() * wholeHeight;
		playerRadiusArray  [i] = 20;
		playerMaxSpeedArray[i] = 6.0;
		playerSpeedArray   [i] = Math.random() * playerMaxSpeedArray[i];
	}
})();

function postInitialState(){
	return 'cellWidth:'+ cellWidth   +';'+
		'cellHeight:'  + cellHeight  +';'+
		'wholeWidth:'  + wholeWidth  +';'+
		'wholeHeight:' + wholeHeight +';';
}

function getFreePlayerId()
{
	if(playerAvailId.length > 0)
		return playerAvailId.pop();
	else
		return -1;
}

function responseInit(obj)
{
	var retObj = {};
	retObj.playerId = getFreePlayerId();
	retObj.pos = {};
	retObj.pos.x = playerPosXArray[retObj.playerId];
	retObj.pos.y = playerPosYArray[retObj.playerId];
	return retObj;
}

function responseUpdate(obj)
{
	var pos = {};
	var retObj = {};
	var playerId = obj.body.playerId;
	var actualWidth = obj.body.actualWidth;
	var actualHeight = obj.body.actualHeight;
	var playerX = playerPosXArray[playerId];
	var playerY = playerPosYArray[playerId];

	var dx = player.body.dirX;
	var dy = player.body.dirY;
	var dist = Math.sqrt(dx*dx+dy*dy);
	var rate = (dist > maxDist) ? 1 : (dist/maxDist);
	var playerSpeed = rate * playerMaxSpeedArray[playerId];

	var finalX = playerX + playerSpeed * dx / dist;
	var finalY = playerY + playerSpeed * dy / dist;

	retObj.pos = [];
	for(var i = 0; i < playerMaxNumber; i++)
	{
		pos.x = playerPosXArray[i];
		pos.y = playerPosYArray[i];
		if(2*Math.abs(pos.x-playerX) < actualWidth
		&& 2*Math.abs(pos.y-playerY) < actualHeight)
			retObj.pos.push(pos);
	}

	if(finalX > 0 && finalX < wholeWidth)
		playerX = playerPosXArray[playerId] = finalX;
	if(finalY > 0 && finalY < wholeHeight)
		playerY = playerPosYArray[playerId] = finalY;

	retObj.player = {"x":playerX, "y":playerY};
	return retObj;
}

/*send and post*/
function postDataToServer(dataFromClient)
{
	/* {"header":"["init, update"]", "body":{}}
	 * update-request {
	 *		"playerId":12,
	 *		"dirX":123,
	 *		"dirY":456,
	 *		"actualWidth":1366,
	 *		"actualHeight":768,
	 *		"zoomRate":1.0	}
	 * update-response {
	 *		"pos":[{x:456, y:789}, {}]
	 * }
	 */
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

function postPosition(playerId, scrWidth, scrHeight){
	/* player and fruit */
	for(var i = 0; i < playerMaxNum; i++)
	{
	}
}
