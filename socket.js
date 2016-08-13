var ws = new WebSocket("ws://127.0.0.1:8080/gamedat")
ws.onopen = function() {
	console.log("init socket...");
}

ws.onmessage = function(evt) {
	console.log(evt.data)
}

function postDataToServer(dataFromClient) {
}
