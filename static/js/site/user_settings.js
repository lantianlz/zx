$(document).ready(function(){
	// 设置日期控件属性
	$('#birthday-id').datetimepicker({
    	format: 'yyyy-mm-dd',
    	language: 'zh-CN',
    	minView: 2,
    	autoclose: true
	});

	// 未使用的邀请链接单击选中全文本
	$('.zx-invitation input').not('.used').bind('click', function(){
		$(this).select();
	});

	// 如果是从个人主页点击进来设置描述信息的时候, 让描述框自动获取焦点
	if(window.location.href.indexOf('#set_des') > -1){
		$('textarea[name=des]').focus();
	}
});