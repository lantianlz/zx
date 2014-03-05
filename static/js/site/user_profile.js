$(document).ready(function(){
	// 左侧切换事件
	$('.stats a').bind('click', function(){
		var target = $(this).attr('href');
		if(target.indexOf('#') > -1){
			$('.user-profile-main a[href='+$(this).attr('href')+']').tab('show');
			$('html,body').animate({scrollTop: 0});
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