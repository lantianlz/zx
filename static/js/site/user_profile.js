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
    $('.user-profile-left .follow').live('click', function(){
        var me = $(this);

    	g_ajax_processing_obj_id = me.setUUID().attr('id');

        $.ZXOperation.followPeople(me.data('user_id'), function(data){
            
            if(data.errcode == 0){
                me.removeClass('follow btn-primary')
                .addClass('unfollow btn-default')
                .text('取消关注');
            } else {
                $.ZXMsg.alert('提示', data.errmsg);
            }
            
        });
    });

    // 用户空间左侧取消关注用户
    $('.user-profile-left .unfollow').live('click', function(){
    	var me = $(this);
        g_ajax_processing_obj_id = me.setUUID().attr('id');

        $.ZXOperation.unfollowPeople(me.data('user_id'), function(data){
            if(data.errcode == 0){
                me.removeClass('unfollow btn-default')
                .addClass('follow btn-primary')
                .text('添加关注');
            } else {
                $.ZXMsg.alert('提示', data.errmsg);
            }
        });
    });

    // 用户空间右侧关注用户
    $('.user-profile-right .follow').live('click', function(){
        var me = $(this);
    	g_ajax_processing_obj_id = me.setUUID().attr('id');

    	$.ZXOperation.followPeople(me.data('user_id'), function(data){
            
            if(data.errcode == 0){
                me.removeClass('follow btn-primary')
                .addClass('unfollow btn-default')
                .text('取消关注');

                // 添加互相关注状态
                me.before('<span class="glyphicon glyphicon-transfer"></span><span class="f12">互相关注</span>');

            } else {
                $.ZXMsg.alert('提示', data.errmsg);
            }
            
        });
    });

    // 用户空间右侧取消关注用户
    $('.user-profile-right .unfollow').live('click', function(){
        var me = $(this);
    	g_ajax_processing_obj_id = me.setUUID().attr('id');

    	$.ZXOperation.unfollowPeople(me.data('user_id'), function(data){
            if(data.errcode == 0){
                me.removeClass('unfollow btn-default')
                .addClass('follow btn-primary')
                .text('添加关注');

                // 删除互相关注状态
                me.prev().remove();
                me.prev().remove();

            } else {
                $.ZXMsg.alert('提示', data.errmsg);
            }
        });
    });
});