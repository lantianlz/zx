
function apply_blogroll()
{
	var postData = {
				   'blogroll_name':$('#blogroll_name').val(),
				   'blogroll_link':$('#blogroll_link').val(),
				   'blogger_email':$('#blogger_email').val(),
				   }
	g_ajax_processing_obj_id = 'apply_blogroll_id';
	ajaxSend('/apply_blogroll', postData, apply_blogroll_callback);
}


function apply_blogroll_callback(data)
{
	if(data['flag'] == '0')
	{
		successMeg('成功');
		$('.simplemodal-close').click();
		window.location.reload();
	}
	else
	{
    	errorMeg(data['result']);
	}
}


function check_friend_name()
{
	var postData = {
				   'friend_name':$('#friend_name').val(),
				   }
	g_ajax_processing_obj_id = 'check_friend_name_id';
	ajaxSend('/check_friend_name', postData, check_friend_name_callback);
}


function check_friend_name_callback(data)
{
	if(data['flag'] == '0')
	{
		successMeg('成功');
		$('.simplemodal-close').click();
		$('#mobilephone').fadeOut('slow').fadeIn('slow').html(data['result']);
	}
	else
	{
    	errorMeg(data['result']);
	}
}



