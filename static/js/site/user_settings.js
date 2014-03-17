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

	// 选择完文件之后自动提交
	$('.avatar-file').bind('change', function(){
		$('.avatar-file').parents('form').submit();
	});

	// 图片剪裁
	var jcropApi,
		cropInfo = {},
        preCon = $('.preview-container'),
        preImg = $('.preview-container img'),
        xsize = preCon.width(),
        ysize = preCon.height();
        updatePreview = function(c){
        	
        	if (parseInt(c.w) > 0){
		        var rx = xsize / c.w;
		        var ry = ysize / c.h;
		        console.log(c)
		        cropInfo = c;

		        preImg.css({
		          	width: Math.round(rx * $('.jcrop-target').width()) + 'px',
		          	height: Math.round(ry * $('.jcrop-target').height()) + 'px',
		          	marginLeft: '-' + Math.round(rx * c.x) + 'px',
		          	marginTop: '-' + Math.round(ry * c.y) + 'px'
		        });
		    }
        };

	if(window.location.href.indexOf('crop_avatar') > -1){
		$('#crop_modal').modal({
			show: true,
			backdrop: 'static'
		});

		$('.jcrop-target').Jcrop({
			onChange: updatePreview,
	      	onSelect: updatePreview,
	      	allowSelect: false,
	      	minSize: [50, 50],
	      	maxSize: [300, 300],
			aspectRatio: xsize / ysize
		}, function(){
			jcropApi = this;
			jcropApi.animateTo([50, 50, 250, 250]);
		});

		$('.btn-crop-save').bind('click', function(){
			//$.ZXMsg.alert('aa', cropInfo.x);
			ajaxSend(
				"/crop_img", {
					'x': cropInfo.x,
					'y': cropInfo.y,
					'w': cropInfo.w,
					'h': cropInfo.h,
				}, function(data){
					if(!data['success']){
						$.ZXMsg.alert('提示', data['msg']);
					} else {
						$('#crop_modal').modal('hide');

						$.ZXMsg.alert('提示', '操作成功!页面即将刷新', 2000);
				        window.setTimeout(function(){
				            window.location = '/account/user_settings';
				        }, 3000);
					}
					
				}
			);
		})
	}

});