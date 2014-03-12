$(function(){
    function loop()
    {
        get_unread_count_total();
        setTimeout(loop, 60000);
    }
    loop();
});


function get_unread_count_total()
{
	var url = '/message/get_unread_count_total';
	ajaxSend(url, '', get_unread_count_total_callback, 'GET');
}


function get_unread_count_total_callback(data)
{
	$('#unread_count_total_nav_1').html(data['result']);
	$('#unread_count_total_nav_2').html(data['result']);
	if(String(data['result']) == '0')
	{
		$('#unread_count_total_nav_1').hide();
		$('#unread_count_total_nav_2').hide();
	}
	else
	{
		$('#unread_count_total_nav_1').show();
		$('#unread_count_total_nav_2').show();
		document.title = '收到 ' + data['result'] + ' 条新消息';
	}
}

/**

// 拉取未读消息提示
var flashTitleInterval = null,
	flashTitleFun = function(){
		var msg = String.format("收到 {0} 条新消息", $('#unread_count_total_nav_1').html());
		if(document.title.indexOf("【新消息】") > -1){
			document.title = msg;
		} else {
			document.title = "【新消息】" + msg;
		}
	},
	getUnreadCountTotal = function(){
    	ajaxSend("/message/get_unread_count_total", '', function(data){
    		$('#unread_count_total_nav_1').html(data['result']);
			$('#unread_count_total_nav_2').html(data['result']);

			if(String(data['result']) == '0'){
				$('#unread_count_total_nav_1').hide();
				$('#unread_count_total_nav_2').hide();
				// if(flashTitleInterval){
				// 	window.clearInterval(flashTitleInterval);
				// }
			} else {
				$('#unread_count_total_nav_1').show();
				$('#unread_count_total_nav_2').show();
				document.title = String.format("收到 {0} 条新消息", data['result'])

				// 有新消息闪烁提示
				// if(!flashTitleInterval){
				// 	flashTitleInterval = window.setInterval(flashTitleFun, 1000);
				// }
				
			}
    	});
    };

// 登录后才轮循
if(CURRENT_USER_ID){
	window.setInterval(getUnreadCountTotal, 60000);
	getUnreadCountTotal();
}
**/