
/*
	为字符串拓展format方法
	用例：
	String.format('{0}, {1}!', 'Hello', 'world')
*/
if (!String.format) {
	String.format = function(src){
	    if (arguments.length == 0){
	    	return null;
	   	}

	    var args = Array.prototype.slice.call(arguments, 1);
	    return src.replace(/\{(\d+)\}/g, function(m, i){
	        return args[i];
	    });
	};
}


/*
  自动补零
*/
function addZero(data){
	var temp = data + '';
	if(temp.length === 0){
		return '00'
	} else if(temp.length === 1){
		return  '0' + temp;
	} else{
		return data;
	}
}


/*
	拓展Jquery方法 
*/
(function(){
	// 设置文本框光标位置
	$.fn.setSelection = function(selectionStart, selectionEnd) {
	    if(this.length == 0){
	    	return this;
	    }

	    input = this[0];

	    // IE
	    if (input.createTextRange) {
	        var range = input.createTextRange();
	        range.collapse(true);
	        range.moveEnd('character', selectionEnd);
	        range.moveStart('character', selectionStart);
	        range.select();
	    } else if (input.setSelectionRange) {
	        input.focus();
	        input.setSelectionRange(selectionStart, selectionEnd);
	    }

	    return this;
	}

	// 设置文本框光标到最后
	$.fn.focusEnd = function() {
	    return this.setSelection(this.val().length, this.val().length);
	}

	// 自定义checkbox
	$.fn.zxCheckbox = function(){

		this.find('input').live('change', function(){
			var parent = $(this).parent();
			
			parent.hasClass('checked') ? parent.removeClass('checked') : parent.addClass('checked');
		});

		return this;
	}

	// 自定义radio
	$.fn.zxRadio = function(){

		this.find('input').live('change', function(){
			
			$('input[name='+$(this).attr('name')+']').each(function(){
				var me = $(this), parent = me.parent();
				
				me.attr('checked') ? parent.addClass('checked') : parent.removeClass('checked');
			});
			
		});

		return this;
	}

})(jQuery);



// 文本编辑器默认设置
var markItUpSettings = {
    onShiftEnter:   {keepDefault:false, replaceWith:'<br />\n'},
    onCtrlEnter:    {keepDefault:false, openWith:'\n<p>', closeWith:'</p>'},
    onTab:        {keepDefault:false, replaceWith:'    '},
    markupSet:  [   
		{name:'粗体', key:'B', openWith:'<b>', closeWith:'</b>' },
		{name:'斜体', key:'I', openWith:'<i>', closeWith:'</i>'  },
		{name:'下划线', key:'U', openWith:'<u>', closeWith:'</u>' },
		{separator:'---------------' },
		{name:'无序列表', openWith:'    <li>', closeWith:'</li>', multiline:true, openBlockWith:'<ul>\n', closeBlockWith:'\n</ul>'},
		{name:'有序列表', openWith:'    <li>', closeWith:'</li>', multiline:true, openBlockWith:'<ol>\n', closeBlockWith:'\n</ol>'},
		{separator:'---------------' },
		{name:'插入图片', key:'P', replaceWith:'<img src="[![Source:!:http://]!]" alt="[![Alternative text]!]" />' },
		{name:'插入链接', key:'L', openWith:'<a href="[![Link:!:http://]!]"(!( title="[![Title]!]")!)>', closeWith:'</a>', placeHolder:'Your text to link...' },
		{separator:'---------------' },
		{name:'清除样式', className:'clean', replaceWith:function(markitup) { return markitup.selection.replace(/<(.*?)>/g, "") } }
		//,{name:'Preview', className:'preview',  call:'preview'}
    ]
};


$(document).ready(function(){
	// 回到顶部动画效果
	var userClickTop = false;

	$(window).scroll(function(){
		var me = $(this);

		if(!userClickTop){
			if(me.scrollTop() < 400){
				$('.scroll-top').hide('fast');
			}else{
				$('.scroll-top').show('fast');
			}
		}
	});

	$('.scroll-top').bind('mouseover', function(){
		var me = $(this);
		if(userClickTop){
			return;
		}

		me.animate({'opacity': '0.3'}, 200, function(){
			//me.css({'background-position-x': -149});
			me.css('background-position', '-149px 0');

			me.animate({'opacity': '0.99'}, 200);
		});
		
	})
	.bind('mouseout', function(){
		var me = $(this);
		if(userClickTop){
			return;
		}

		me.animate({'opacity': '0.3'}, 200, function(){
			//me.css({'background-position-x': 0});
			me.css('background-position', '0 0');

			me.animate({'opacity': '0.99'}, 200);
		});
		
	})
	.bind('click', function(){
		var me = $(this);
		userClickTop = true;
		me.css('background-position', '-298px 0');
		$('html,body').animate({scrollTop:0}, 'fast', function(){
			me.animate({'bottom': 800}, 500, function(){
				me.css({'bottom': 10}).hide();
				me.css('background-position', '0 0');
				userClickTop = false;
			});
		}); 
		
	});


	// 给不支持placeholder的浏览器添加此属性
  	$('input, textarea').placeholder();

	// 初始化所有的 tooltip 
	//$('.zx-tooltip').tooltip('hide');
	$('.zx-tooltip').tooltipsy({
	    offset: [1, 0],
	    css: {
	        'padding': '10px',
	        'max-width': '200px',
	        'color': '#fff',
	        'background-color': '#000',
	        'border': '1px solid #deca7e',
	        '-moz-box-shadow': '0 0 10px rgba(0, 0, 0, .5)',
	        '-webkit-box-shadow': '0 0 10px rgba(0, 0, 0, .5)',
	        'box-shadow': '0 0 10px rgba(0, 0, 0, .5)',
	        'border-radius': '4px',
	        'font-size': '12px'
	    }
	});
	
	// 初始化所有的 popover 
	//$('.zx-popover').popover('hide');
	

	// 弹出名片设置
	var cardtipsHtml = '<div class="cardtips"><div class="profile row"><div class="col-md-3"><img class="avatar avatar-circle" src="{0}" ></div><div class="col-md-9"><div class="username">{1}</div><div class="question-info"><span>提问<a href="#">{2}</a></span><span>回答<a href="#">{3}</a></span><span>赞<a href="#">{4}</a></span></div></div></div><div class="desc">{5}</div><div class="tools"><button type="button" class="btn btn-primary btn-xs follow {8}">关注ta</button><button type="button" class="btn btn-default btn-xs unfollow {9}">取消关注</button><a class="send-message" href="#" data-user_name="{6}" data-user_id="{7}"><span class="glyphicon glyphicon-envelope"></span> 私信ta</a></div></div>'
	$('.zx-cardtips1').tooltipster({
		animation: 'fade',
		delay: 200,
		trigger: 'hover',
		theme: 'tooltipster-shadow',
		interactive: true,
		interactiveTolerance: 300,
		autoClose: true,
		//content: cardtipsHtml,
		contentAsHTML: true,
		content: '名片加载中...',
	    functionBefore: function(origin, continueTooltip) {

	        // we'll make this function asynchronous and allow the tooltip to go ahead and show the loading notification while fetching our data
	        continueTooltip();
	        
	        // next, we want to check if our data has already been cached
	        if (origin.data('ajax') !== 'cached') {
	            $.ajax({
	                type: 'POST',
	                dataType: 'json',
	                url: '/account/get_user_info_by_id?user_id=' + origin.data('user_id'),
	                success: function(data) {
	                    if(data.success){
		                    origin.tooltipster('content', String.format(
		                    	cardtipsHtml, 
		                    	data.avatar,
		                    	data.name, 
		                    	data.question_count,
		                    	data.answer_count,
		                    	data.like_count,
		                    	data.desc,
		                    	data.name,
		                    	data.id,
		                    	data.is_follow?'hide':'', // 关注按钮
		                    	data.is_follow?'':'hide' //取消关注按钮
		                    )).data('ajax', 'cached');
	                    } else {
	                    	origin.tooltipster('content', '加载名片失败');
	                    }
	                }
	            });
	        }
	    }
	});
	// 从名片上点击发私信事件 
	$('.send-message').live('click', function(){
		var user_name = $(this).data('user_name');
		var user_id = $(this).data('user_id');
		$('#new_message_modal').modal('show')

		$('#receiver_label').text(user_name);
		$('#receiver_id').val(user_id);
	})


	/*
	// 设置编辑器
  	$('.zx-textarea').markItUp(markItUpSettings);
  	// 设置文本框自动增加高度
  	$('.zx-textarea').bind('keyup', function(e){
		if(e.keyCode == 13){
			$(this).height($(this).height() + $(this).scrollTop() + 2);
		}
	});
	*/


  	
	/*
	// KindEditor 编辑器设置
	var editor;
	KindEditor.ready(function(K) {
	    editor = K.create('.zx-textarea', {
			resizeType : 1,
			width: '100%',
			height: '260',
			allowPreviewEmoticons : false,
			allowImageUpload : false,
			themesPath: MEDIA_URL + "css/kindeditor/themes/",
			pluginsPath: MEDIA_URL + "js/kindeditor/plugins/",
			langPath: MEDIA_URL + "js/kindeditor/",
			items : [
				'bold', 'italic', 'underline', 'removeformat', '|', 
				'justifyleft', 'justifycenter', 'justifyright', 'insertorderedlist', '|', 
				'image', 'link', '|', 
				'fullscreen'
			],
			afterCreate : function() { 
			  	this.sync(); 
			}, 
			afterBlur:function(){ 
			  	this.sync(); 
			}
	    });
	});
	*/
    

    /* UE
    var ue = UE.getEditor('zx-editor', {
        toolbars: [[
         	'bold', 'italic', 'underline', 'removeformat', '|',
            'insertorderedlist', 'insertunorderedlist', '|' ,
            'link', 'unlink', 'insertimage', 'insertvideo', '|',
            'preview', 'cleardoc', 'fullscreen'
        ]],
        dropFileEnabled: false,
        pasteplain: true
    });

    var ue2 = UE.getEditor('zx-editor2', {
        toolbars: [
            'bold', 'italic', 'underline', 'removeformat', '|',
            'insertorderedlist', 'insertunorderedlist', '|' ,
            'link', 'unlink', 'insertimage', 'insertvideo', '|',
            'preview', 'cleardoc', 'fullscreen'
        ],
        initialFrameWidth: '100%',
        dropFileEnabled: false,
        pasteplain: true
    });
	*/

	// UM
    var um = UM.getEditor('zx-editor', {
        toolbar:[
            'bold italic underline removeformat |',
            'insertorderedlist insertunorderedlist |' ,
            'link unlink image insertvideo  |',
            'preview cleardoc fullscreen'
        ],
        dropFileEnabled: false
    });

    var um2 = UM.getEditor('zx-editor2', {
        toolbar:[
            'bold italic underline removeformat |',
            'insertorderedlist insertunorderedlist |' ,
            'link unlink image insertvideo  |',
            'preview cleardoc fullscreen'
        ],
        initialFrameWidth: '100%',
        dropFileEnabled: false
    });
	

    
    // 鼠标移动到导航条登录用户名时自动弹出下拉框
    var dropdownTimeout = null,
    	showDropdown = function(){
	    	$(".login-user .dropdown").addClass('open');

	    	if(dropdownTimeout){
	    		window.clearTimeout(dropdownTimeout);
	    		dropdownTimeout = null;
	    	}
	    },
    	hideDropdown = function(){
	    	if(!dropdownTimeout){
	    		dropdownTimeout = window.setTimeout(function(){
	    			$(".login-user .dropdown").removeClass('open');
	    			dropdownTimeout = null;
	    		}, 1000)
	    	}
   		};
    
    $('.login-user .dropdown-toggle')
    .bind('mouseenter', showDropdown)
    .bind('mouseleave', hideDropdown);

    $('.login-user .dropdown-menu')
    .bind('mouseenter', showDropdown)
    .bind('mouseleave', hideDropdown);

    // 隐藏所有 auto-hide 样式
    $('.auto-hide').hide();


    // 拉取未读消息提示
    var flashTitleInterval = null,
    	flashTitleFun = function(){
    		var msg = String.format("收到 {0} 条新消息", $('#unread_count_total_nav_1').html());
    		if(document.title.indexOf("【新消息】") > -1){
    			document.title = msg;
    		} else {
    			document.title = "【新消息】" + msg;
    		}
    	},
    	getUnreadCountTotal = function(){
	    	ajaxSend("/message/get_unread_count_total", '', function(data){
	    		$('#unread_count_total_nav_1').html(data['result']);
				$('#unread_count_total_nav_2').html(data['result']);

				if(String(data['result']) == '0'){
					$('#unread_count_total_nav_1').hide();
					$('#unread_count_total_nav_2').hide();
					if(flashTitleInterval){
						window.clearInterval(flashTitleInterval);
					}
				} else {
					$('#unread_count_total_nav_1').show();
					$('#unread_count_total_nav_2').show();

					// 有新消息闪烁提示
					if(!flashTitleInterval){
						flashTitleInterval = window.setInterval(flashTitleFun, 1000);
					}
					
				}
	    	});
	    };

    // 登录后才轮循
    if(CURRENT_USER_ID){
    	window.setInterval(getUnreadCountTotal, 60000);
    	getUnreadCountTotal();
    }
    
});

