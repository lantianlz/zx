$(document).ready(function(){
	// var showTab = function(tabName){
	// 	$('.user-profile-main a[href='+tabName+']').tab('show');
	// 	$('html,body').animate({scrollTop: 0});
	// }

	// // 根据锚点切换到指定的tab
	// if(window.location.href.indexOf('#') > -1){
	// 	showTab('#' + window.location.href.split('#')[1]);
	// }

	// 左侧切换事件
	// $('.stats a').bind('click', function(){
	// 	var target = $(this).attr('href');
	// 	if(target.indexOf('#') > -1){
	// 		showTab($(this).attr('href'));
	// 	}
		
	// });


	// 鼠标移动到头像旋转事件
	$('.avatar-100')
	.bind('mouseenter', function(){
		$(this).addClass('avatar-spin');
	})
	.bind('mouseleave', function(){
		$(this).removeClass('avatar-spin');
	});


	// 关注话题事件
	$('.topic-item .btn-follow').bind('click', function(){
        var target = $(this).parents('.topic-item').eq(0).find('.zx-topictips');

        $.ZXMsg.alert('关注话题', target.data('topic_id'));
    });
    // 取消关注话题事件
    $('.topic-item .btn-unfollow').bind('click', function(){
        var target = $(this).parents('.topic-item').eq(0).find('.zx-topictips');

        $.ZXMsg.alert('取消关注话题', target.data('topic_id'));
    });


    // 用户空间左侧关注用户
    $('.user-profile-left .follow').bind('click', function(){
    	g_ajax_processing_obj_id = 'left_follow_button_id';
    	$.ZXOperation.followPeople($(this).data('user_id'), common_callback);
    });

    // 用户空间左侧取消关注用户
    $('.user-profile-left .unfollow').bind('click', function(){
    	g_ajax_processing_obj_id = 'left_unfollow_button_id';
    	$.ZXOperation.unfollowPeople($(this).data('user_id'), common_callback);
    });

    // 用户空间右侧关注用户
    $('.user-profile-right .follow').bind('click', function(){
    	g_ajax_processing_obj_id = 'right_follow_button_id_' + $(this).data('user_id');
    	$.ZXOperation.followPeople($(this).data('user_id'), common_callback);
    });

    // 用户空间右侧取消关注用户
    $('.user-profile-right .unfollow').bind('click', function(){
    	g_ajax_processing_obj_id = 'right_unfollow_button_id_' + $(this).data('user_id');
    	$.ZXOperation.unfollowPeople($(this).data('user_id'), common_callback);
    });
});