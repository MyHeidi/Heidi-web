var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    //socket.emit('my event', {data: 'I\'m connected!'});
    console.log("Established socket.io connection");
});

var debugLogList = $('#debug-log-list');

socket.on('log', function(data) {
    console.log('socket->log', data);

    if (debugLogList.length == 0) {
        return;
    }

    var item = $('<ul>');
    item.text(data);
    item.addClass('list-group-item');
    debugLogList.prepend(item);
});

var logList = $('#log-list');

var prependLogItem = function(action, text) {
    if (logList.length == 0) {
        return;
    }

    var html = $('<strong>').text(action) + text;
    return $('<ul>').html(html).addClass('list-group-item')
};

socket.on('update_location', function(data) {
    console.log('io -> update_location', data);
    prependLogItem("update_location", "test");
});

socket.on('get_question', function(data) {
    console.log('io -> get_question', data);
    prependLogItem("get_question", "test");
});

$('.btn-send-get').click(function() {
    var $this = $(this);
    var href = $this.prop('href');
    $.get(href, function(response) {
        console.log('GET ' + href + ' success', response);
    });

    return false;
});
