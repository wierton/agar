(function(){
	var itemMaxNum      = 500;
	var itemActualNum = 0;
	var itemXArray = new Array(itemMaxNum);
	var itemYArray = new Array(itemMaxNum);
	var itemRArray = new Array(itemMaxNum);
	var cellWidth   = 500;
	var cellHeight  = 500;
	var wholeWidth  = 2000;
	var wholeHeight = 2000;
	var availWidth  = document.documentElement.clientWidth;
	var availHeight = document.documentElement.clientHeight;
	var zoomRate    = 1.0;
	var ctx         = undefined;

	var mouseX       = wholeWidth / 2;
	var mouseY       = wholeHeight / 2;
	var playerX      = 0;
	var playerY      = 0;
	var playerId     = 0;
	var playerRadius = 0;
	var playerColor  = "#235689";
	var playerSpeed  = 4.5;
	var playerMaxSpeed = 6.0;
	var updateDataFromServer = {};

	var frameNumber  = 40;

	var ws = new WebSocket("ws://127.0.0.1:8081/gamedat");
	ws.onmessage = getDataFromServer;

	$(document).ready(function(){
		$("#canvas").attr({
			"width":'' + document.documentElement.clientWidth,
			"height":'' + document.documentElement.clientHeight
		});
		initFromServer();
		ctx = document.getElementById("canvas").getContext("2d");
		window.onresize = resizeCanvas;
		document.onmousemove = moveMouse;
		drawBack();
		ws.send('qweasd');
	})
	
	setInterval("this.mainLogic()", 1000 / frameNumber);

	function test()
	{
		var testEnemy = [];
		for(var i = 0; i < 10; i++)
		{
			var item = {};
			item.x = Math.random();
			item.y = Math.random();
			testEnemy.push(item);
		}

		for(var i = 0; i < testEnemy.length; i++)
		{
			console.log(i + ' ' + testEnemy[i].x + " " + testEnemy[i].y);
		}
	}

	function initFromServer()
	{
		var data = '{"header":"init"}';
		var retStr = postDataToServer(data);
		var retObj = JSON.parse(retStr);
		playerId = retObj.playerId;
		playerX = retObj.pos.x;
		playerY = retObj.pos.y;
		playerRadius = retObj.playerRadius;
	}

	function resizeCanvas(e) {
		$("#canvas").attr({
			"width":'' + window.innerWidth,
			"height":'' + window.innerHeight
		});

		var dx = (window.innerWidth - availWidth)/2;
		var dy = (window.innerHeight - availHeight)/2;
		availWidth  = window.innerWidth;
		availHeight = window.innerHeight;
		refreshCanvas();
	}

	function drawBack(){
		var toUp = function(value) {
			return parseInt((value + (zoomRate * cellWidth)) / (zoomRate * cellWidth)) * (zoomRate * cellWidth);
		}
		borderStartX = playerX < (availWidth / 2) ? ((availWidth / 2) - playerX) : (toUp(playerX - availWidth / 2) - (playerX - availWidth / 2));
		borderStartY = playerY < (availHeight / 2) ? ((availHeight / 2) - playerY) : (toUp(playerY - availHeight / 2) - (playerY - availHeight / 2));
		ctx.fillStyle = "black";
		ctx.strokeStyle = "black";
		ctx.fillRect(0, 0, availWidth, availHeight);
		ctx.fillStyle = "#222222";
		for(i = borderStartX; i <= availWidth; i += zoomRate * cellWidth)
		{
			ctx.fillRect(i, 0, 1, availHeight);
		}
		for(j = borderStartY; j <= availHeight; j += zoomRate * cellHeight)
		{
			ctx.fillRect(0, j, availWidth, 1);
		}
	}

	function drawItem(x, y, r) {
		ctx.fillStyle = playerColor;
		ctx.beginPath();
		ctx.arc(x, y, r, 0, 2*Math.PI);
		ctx.closePath();
		ctx.fill();
	}

	function drawPlayer() {
		ctx.fillStyle = playerColor;
		ctx.arc(availWidth/2, availHeight/2, playerRadius, 0, 2*Math.PI);
		ctx.fill();
	}

	function moveMouse(e) {
		var ev = e || window.event;
		mouseX = ev.clientX;
		mouseY = ev.clientY;
	}

	function movePlayer() {
		var rate = 0;
		var maxDist = Math.sqrt(availWidth*availWidth+availHeight*availHeight)/2;
		var dx = mouseX - availWidth/2;
		var dy = mouseY - availHeight/2;
		var mouseDist = Math.sqrt(dx*dx+dy*dy);
		if(mouseDist > maxDist / 2)
			rate = 1;
		else
			rate =2*mouseDist/maxDist;
		playerSpeed = playerMaxSpeed * rate;
		if(playerSpeed > 0.1)
		{
			var finalX = playerX + playerSpeed * dx / mouseDist;
			var finalY = playerY + playerSpeed * dy / mouseDist;
			if(finalX > 0 && finalX < wholeWidth)
				playerX = finalX;
			if(finalY > 0 && finalY < wholeHeight)
				playerY = finalY;
		}
	}

	function refreshCanvas() {
		drawBack();
		drawPlayer();
	}

	function updateFromServer()	{
		var tmp = '';
		var data = {
			"header":"update",
			"body"  : {
				"playerId":playerId,
				"dirX"    :(mouseX - availWidth/2),
				"dirY"    :(mouseY - availHeight/2),
				"actualWidth" :(zoomRate * availWidth),
				"actualHeight":(zoomRate * availHeight),
				"zoomRate"    :zoomRate
			}
		};
		data = JSON.stringify(data);
		tmp = postDataToServer(data);
		updateDataFromServer = JSON.parse(tmp);
		/*
		$.post('gamedat', data, function(data, statu){
			console.log(statu + data);
		});
		*/
	}

	function getDataFromServer(evt)
	{
	}

	function parseDataFromServer() {
		var lene = updateDataFromServer.enemy.length;
		var lfru = updateDataFromServer.fruit.length;
		var halfAvailWidth  = availWidth / 2;
		var halfAvailHeight = availHeight / 2;
		playerX = updateDataFromServer.player.x;
		playerY = updateDataFromServer.player.y;
		playerRadius = updateDataFromServer.r;
		itemActualNum = lene + lfru;
		itemActualNum = itemActualNum < itemMaxNum ? itemActualNum : itemMaxNum;
		for(var i = 0; i < lene; i++)
		{
			itemXArray[i] = updateDataFromServer.enemy[i].x - playerX + halfAvailWidth;
			itemYArray[i] = updateDataFromServer.enemy[i].y - playerY + halfAvailHeight;
			itemRArray[i] = updateDataFromServer.enemy[i].r;
		}
		for(var i = 0; i < lfru; i++)
		{
			itemXArray[i+lene] = updateDataFromServer.fruit[i].x - playerX + halfAvailWidth;
			itemYArray[i+lene] = updateDataFromServer.fruit[i].y - playerY + halfAvailHeight;
			itemRArray[i+lene] = 5;
		}
	}

	function displayParsedData() {
		for(var i = 0; i < itemActualNum; i++)
		{
			drawItem(itemXArray[i], itemYArray[i], itemRArray[i]);
		}
	}

	this.mainLogic = function() {
		drawBack();
		drawPlayer();
		updateFromServer();
		parseDataFromServer();
		displayParsedData();
	}
})();
