$(function(){
    function loop()
    {
        get_unread_count_total('{{request.user.id}}');
        setTimeout(loop, 60000);
    }
    loop();
});


function get_unread_count_total(user_id)
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
	}
}
