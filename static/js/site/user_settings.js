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
});