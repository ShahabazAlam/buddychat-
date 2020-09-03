let NotificationSocket = new ReconnectingWebSocket(
    'ws://' + window.location.host +
    '/ws/all_notifications/');

NotificationSocket.onopen = function (e) {
    fetchNotifications()
};
// friend request related notifications

$("#unread_notifications").on('click',function(){
    $("#read_li_notifications").removeAttr('class','uk-active')
    $("#unread_li_notifications").attr('class','uk-active')
    $("#notifications_list").html('')
    fetchNotifications()
})

$("#read_notifications").on('click',function(){
    $("#notifications_list").html('')
    $("#unread_li_notifications").removeAttr('class','uk-active')
    $("#read_li_notifications").attr('class','uk-active')
    NotificationSocket.send(JSON.stringify({'command': 'fetch_read_friends_notifications'}));
})

$("#remove_all_unread").on('click',function(){
    NotificationSocket.send(JSON.stringify({'command': 'remove_all_unread_notifications'}));
})

$("#remove_all_read").on('click',function(){
    NotificationSocket.send(JSON.stringify({'command': 'remove_all_read_notifications'}));
})


NotificationSocket.onmessage = function (event) {
    let data = JSON.parse(event.data);
    if (data['command'] === 'notifications') {
        let notifications = JSON.parse(data['notifications']);
        $('#r_count').html('<span id="notify_num">'+notifications.length+'</span>');
        if(notifications.length == 0){
          $('#notify_num').hide()
          $('#n_read_options').hide()
          $('#n_unread_options').hide()  
        }
        for (let i = 0; i < notifications.length; i++) {
            Notifications(notifications[i]);
        }
    }

    else if (data['command'] === 'read_notifications') {
        let notifications = JSON.parse(data['notifications']);
        if(notifications.length == 0){
            $('#n_read_options').hide() 
          }else{
              $('#n_read_options').show()
          }
        for (let i = 0; i < notifications.length; i++) {
            Notifications(notifications[i]);
    }
        


    } else if (data['command'] === 'new_friend_request_notification')     {
        let notification = $('#notify_num');
        $('#notify_num').text(parseInt(notification.text()) + 1);
        if(parseInt(notification.text()) > 0){
            $('#notify_num').fadeIn()
            $('#n_unread_options').show() 
        }
        Notifications(JSON.parse(data['notification']));


    }else if (data['command'] === 'new_accept_request_notification') {        
        let notification = $('#notify_num');
        $('#notify_num').text(parseInt(notification.text()) + 1);        
        if(parseInt(notification.text()) > 0){
            $('#notify_num').fadeIn()
            $('#n_unread_options').show() 
        }
        Notifications(JSON.parse(data['notification']));


    }else if (data['command'] === 'removed_unread_notifications') {
            $("#notifications_list").html('')
            $('#r_count').html('')
            $('#n_unread_options').hide()


    }else if (data['command'] === 'removed_read_notifications') {
            $("#notifications_list").html('')
            $('#n_read_options').hide()
    }
};

function fetchNotifications() {
    NotificationSocket.send(JSON.stringify({'command': 'fetch_friends_notifications'}));
}

function Notifications(notification) {
    var d_p = '';
    var button = '';
    if(notification.actor.profileImage != null){
        d_p = '<img src="/media/profileImages/'+notification.actor.profileImage+'"  alt="not" />';
    }
    else{
        if(notification.actor.gender != 'male'){
            d_p = '<img src="/static/gender/female.jpg"  alt="not" />';
        }
        else{ d_p = '<img src="/static/gender/male.jpg"  alt="not" />'; }
    }
    if(notification.verb === 'accepted your friend request'){
        button = ''
    }else if (notification.verb === 'sent you friend request' && notification.unread == 1){
        button = ` <a class="button primary small accept-request" onclick="accept(this,${notification.id})" data-friend="${notification.actor.id}">Accept</a>
                    <a class="button danger small" onclick="reject(this,${notification.id})" data-friend="${notification.actor.id}">Reject</a>`
    }
    var time = new Date(notification.timestamp);
    var n_time = TimeAgo.inWords(time.getTime());
    let single = `<div id="n_list${notification.id}" style="border-radius: 10px;">
                    <li>
                        <a href="#">
                            <span class="message-avatar">
                                ${d_p}
                            </span>
                            <span class="notification-text">
                                <strong>${notification.actor.first_name} ${notification.actor.last_name}</strong> ${notification.verb}
                                <span class="text-primary"></span>
                                <br> <span class="time-ago">${n_time}</span>
                            </span>
                        </a>
                    </li>
                ${button}
            </div>`;
    $('#notifications_list').prepend(single);

    if (notification.verb === 'accepted your friend request')
    {
        $("#n_list"+notification.id).attr("onclick",`read(${notification.id},${notification.actor.id})`);
    }
}


// function read notification
function read(id,user_id){
    let url = '/notifications/mark-notification-as-read';
    $.ajax({
        type: 'GET',
        url: url,
        data:{'id':id},
        success: (function () {
            var notification = $('#notify_num');
            $('#notify_num').text(parseInt(notification.text()) - 1);
            if(parseInt(notification.text()) == 0){
             $('#notify_num').hide()}
            $("#n_list"+id).fadeOut()
            window.location.href = '/profile/user_timeline/'+user_id;
        }),
        error: (function (err) {
            console.log(err);
        })
    });
}

// function accept request
function accept(li,li_id) {
    let friend = $(li).data('friend');

    let url = `/friends/accept-request/${friend}`;

    $.ajax({
        type: 'GET',
        url: url,
        success: (function () {
            var notification = $('#notify_num');
            $('#notify_num').text(parseInt(notification.text()) - 1);
            if(parseInt(notification.text()) == 0){
            $('#notify_num').hide()
            $('#n_unread_options').hide()}
            $("#n_list"+li_id).fadeOut()
        }),
        error: (function (err) {
            console.log(err);
        })
    });
}
//cancel request function
    function reject(li,li_id){
        let friend = $(li).data('friend');

        let url = `/friends/cancel-request/${friend}`;
         $.ajax({
                url:url,
                type:'GET',
                success:(function() {
                    var notification = $('#notify_num');
                    $('#notify_num').text(parseInt(notification.text()) - 1);
                    if(parseInt(notification.text()) == 0){
                        $('#notify_num').hide()}
                    $("#n_list"+li_id).fadeOut()
             }),
             error: (function (err) {
                console.log(err);
        })
        })
    }