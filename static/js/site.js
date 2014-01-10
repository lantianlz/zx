
function apply_blogroll()
{
	var postData = {
				   'blogroll_name':$('#blogroll_name').val(),
				   'blogroll_link':$('#blogroll_link').val(),
				   'blogger_email':$('#blogger_email').val(),
				   }
	g_ajax_processing_obj_id = 'apply_blogroll_id';
	ajaxSend('/apply_blogroll', postData, apply_blogroll_callback);
}


function apply_blogroll_callback(data)
{
	if(data['flag'] == '0')
	{
		successMeg('成功');
		$('.simplemodal-close').click();
		window.location.reload();
	}
	else
	{
    	errorMeg(data['result']);
	}
}


function check_friend_name()
{
	var postData = {
				   'friend_name':$('#friend_name').val(),
				   }
	g_ajax_processing_obj_id = 'check_friend_name_id';
	ajaxSend('/check_friend_name', postData, check_friend_name_callback);
}


function check_friend_name_callback(data)
{
	if(data['flag'] == '0')
	{
		successMeg('成功');
		$('.simplemodal-close').click();
		$('#mobilephone').fadeOut('slow').fadeIn('slow').html(data['result']);
	}
	else
	{
    	errorMeg(data['result']);
	}
}



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


	// 初始化所有的 tooltip 
	$('.zx-tooltip').tooltip('hide');
});

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