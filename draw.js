(function(){
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
	var playerX      = wholeWidth / 2;
	var playerY      = wholeHeight / 2;
	var playerRadius = 50;
	var playerColor  = "#235689";
	var playerSpeed  = 4.5;
	var playerMaxSpeed = 6.0;

	var frameNumber  = 20;

	$(document).ready(function(){
		$("#canvas").attr({
			"width":'' + document.documentElement.clientWidth,
			"height":'' + document.documentElement.clientHeight
		});
		ctx = document.getElementById("canvas").getContext("2d")
		window.onresize = resizeCanvas;
		document.onmousemove = moveMouse;
	})
	
	setInterval("this.mainLogic()", 1000 / frameNumber);

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

	console.log("Hello World!\n");
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

	function drawFood(x, y) {
		ctx.fillStyle = playerColor;
		ctx.arc(availWidth/2, availHeight/2, playerRadius, 0, 2*Math.PI);
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

	this.mainLogic = function() {
		movePlayer();
		drawBack();
		drawPlayer();
	}

})();
