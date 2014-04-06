$(document).ready(function(){
	var showTab = function(tabName){
		$('.user-profile-main a[href='+tabName+']').tab('show');
		$('html,body').animate({scrollTop: 0});
	}

	// 根据锚点切换到指定的tab
	if(window.location.href.indexOf('#') > -1){
		showTab('#' + window.location.href.split('#')[1]);
	}

	// 左侧切换事件
	$('.stats a').bind('click', function(){
		var target = $(this).attr('href');
		if(target.indexOf('#') > -1){
			showTab($(this).attr('href'));
		}
		
	});

	// 鼠标移动到头像旋转事件
	$('.avatar-100')
	.bind('mouseenter', function(){
		$(this).addClass('avatar-spin');
	})
	.bind('mouseleave', function(){
		$(this).removeClass('avatar-spin');
	});

	$('.topic-item .btn-follow').bind('click', function(){
        var target = $(this).parents('.topic-item').eq(0).find('.zx-topictips');

        $.ZXMsg.alert('关注话题', target.data('topic_id'));
    });
    $('.topic-item .btn-unfollow').bind('click', function(){
        var target = $(this).parents('.topic-item').eq(0).find('.zx-topictips');

        $.ZXMsg.alert('取消关注话题', target.data('topic_id'));
    })
});