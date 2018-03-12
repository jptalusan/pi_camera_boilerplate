$(document).ready(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var toggle = false;
    socket.on('connect', function() {
        socket.emit('client_connected', {data: 'new client!'});
    });

    $("#start").click(function() {
        console.log('starting bench...');
        socket.emit('button_pressed', 0);
        if (toggle) {
            toggle = false;
            $("#start").html('Start sending');
        } else {
            toggle = true;
            $("#start").html('Stop sending');
        }
    });
});
