$(document).ready(function(){
	var showTab = function(tabName){
		$('.user-profile-main a[href='+tabName+']').tab('show');
		$('html,body').animate({scrollTop: 0});
	}

	if(window.location.href.indexOf('#questions') > -1){
		showTab('#questions');
	}

	if(window.location.href.indexOf('#answers') > -1){
		showTab('#answers');
	}

	// 左侧切换事件
	$('.stats a').bind('click', function(){
		var target = $(this).attr('href');
		if(target.indexOf('#') > -1){
			showTab($(this).attr('href'));
		}
		
	});

	$('.avatar-100')
	.bind('mouseenter', function(){
		$(this).addClass('avatar-spin');
	})
	.bind('mouseleave', function(){
		$(this).removeClass('avatar-spin');
	});
});