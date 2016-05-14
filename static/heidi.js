var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    socket.emit('my event', {data: 'I\'m connected!'});
});

var logList = $('#log-list');

socket.on('log', function(data) {
    console.log('socket->log', data);

    if (logList.length == 0) {
        return;
    }
    
    var item = $('<ul>');
    item.text(data);
    item.addClass('list-group-item');
    logList.prepend(item);
});

$('.btn-send-get').click(function() {
    var $this = $(this);
    var href = $this.prop('href');
    $.get(href, function(response) {
        console.log('GET ' + href + ' success', response);
    });

    return false;
});
