function timeAgo(time){
    var userEntered = new Date(time); // valueAsNumber has no time or timezone!
    var now = new Date();
    var today = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() ));
    var msgtime = new Date(Date.UTC(userEntered.getUTCFullYear(), userEntered.getUTCMonth(), userEntered.getUTCDate() ));
        
        var h = userEntered.getHours();
        var m = userEntered.getMinutes();
        var x = h >= 12 ? 'pm' : 'am';
        h = h % 12;
        h = h ? h : 12;
        m = m < 10 ? '0'+m: m;
        var mytime= h + ':' + m + ' ' + x;

    if(msgtime.getTime() === (today.getTime() - 86400000))
    {
        return 'yesterday ' + mytime;
    }
    else if(msgtime.getTime() == today.getTime())
    {
            return mytime;
    }
    else if(msgtime.getTime() < (today.getTime() - 86400000)){
            year=userEntered.getFullYear();
            month=userEntered.getMonth();
            day=userEntered.getDate();
            
            return day+"/"+month+"/"+year + ' ' + mytime
    }

}


  // checkOnline function
function checkOnline(id)
{
    var data = ''
    $.ajax({
            url:'/messages/check-online/',
            type:'GET',
            data: {'id':id},
            async: false, 
            success:(function(data) { 
               result = data
            })
    })
    if(result.status == 'online'){
        data = 'status-icon status-online'      
    }
    else
    {  
         data = 'status-icon status-offline'
    }
    return data;
}
  