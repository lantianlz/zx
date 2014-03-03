$(document).ready(function(){
	// 左侧切换事件
	$('.stats a').bind('click', function(){
		$('.user-profile-main a[href='+$(this).attr('href')+']').tab('show');
	});

	$('.avatar-100')
	.bind('mouseenter', function(){
		$(this).addClass('avatar-spin');
	})
	.bind('mouseleave', function(){
		$(this).removeClass('avatar-spin');
	});
});