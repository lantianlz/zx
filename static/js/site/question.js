$(document).ready(function(){
    /*
    var text_tags = new $.TextboxList('#question_tags_input', {
        bitsOptions: {
            box: {deleteButton: true}
        },
        unique: true, 
        max: 10,
        plugins: {
            autocomplete: {
                minLength: 1,
                queryRemote: true,
                placeholder: '添加标签',
                highlight: false,
                remote: {url: '/question/get_tags' }
            }
        }

    });
    //text_tags.add('John Doe').add('Jane Roe');
    */

    
    var askEditor = createEditor('#ask_editor'),
        answerEditor = createEditor('#answer_editor'),
        questionEditor = createEditor('#question_editor'),
        editAnswerEditor = createEditor('#edit_answer_editor');


    // 我要提问 IE 链接不过去问题，强制js跳转
    $('.ask-question button').bind('click', function(){
        window.location.href = '/question/ask_question';
    });


    // 按钮点击事件 IE直接点还不行,非要js
    $('.not-login .btn-login').bind('click', function(){
        window.location.href = '/login';
    });
    $('.not-login .btn-regist').bind('click', function(){
        window.location.href = '/regist';
    });

    // 定位到答案
    if(window.location.href.indexOf('#to_answer_') > -1){
        $('html,body').animate({
            scrollTop: $('#'+window.location.hash.substring('4')).offset().top + ($.browser.msie ? document.documentElement.scrollTop : 0) - parseInt($('.container_content').css('margin-top')) + 15
        });
    }


    // 初始化自定义的zxCheckbox
    $('#div_tags .zx-checkbox').zxCheckbox();
    $('#div_types .zx-radio').zxRadio();


    // 选择问题类型事件
    $('#div_types .zx-radio>input').bind("change", function(){
        $('#div_tags').hide('fast').find('label').remove();

        var type = $(this).val();
        if(!type) {
            return;
        }
        var type_tags = QUESTION_TAGS[type];
        if(!type_tags){
            return;
        }
        $('#div_tags').show('fast');
        for (var i=0; i<type_tags.length; i++) {
            $('#div_tags').append(
                String.format(
                    '<label class="checkbox-inline zx-checkbox"><input name="tag" type="checkbox" value="{0}"> {1}</label>', 
                    type_tags[i][0], 
                    type_tags[i][1]
                )
            );
        };
    });


    // 回答工具条鼠标移动显示隐藏事件
    $('#ul_replies .list-group-item')
    .bind('mouseenter', function(){
        $(this).find('.reply-tools .auto-hide').show();
    })
    .bind('mouseleave', function(){
        $(this).find('.reply-tools .auto-hide').hide();
    });
    // 评论工具条鼠标移动显示隐藏事件
    $('.reply-comments .comment')
    .bind('mouseenter', function(){
        $(this).find('.comment-date .auto-hide').show();
    })
    .bind('mouseleave', function(){
        $(this).find('.comment-date .auto-hide').hide();
    });
    
  
    // 评论打开关闭事件
    $('.reply-tools .answer-comments').bind('click', function(){
        var target = $(this).parent().next();

        target.css('display') === 'block' ? target.hide('fast') : target.show('fast');
    });


    // 邀请打开关闭事件
    $('.question-tools .invite').bind('click', function(){
        var target = $(".topic-invite");
        
        target.css('display') === 'block' ? target.hide() : target.show();
    });
    // 邀请某人回答事件
    $('.recommend-invite .btn-invite').bind('click', function(){
        var target = $(this).parents('.invite-person-info').find('.zx-cardtips');
        $.ZXMsg.alert('邀请某人', target.data('user_id'));
    });
    // 邀请查询事件
    $('.filter-invite .search').bind('click', function(){
        $.ZXMsg.alert('查询某人', $(this).prev().val());
    });

    // 折叠回答打开关闭事件
    $('.collapse-answer').bind('click', function(){
        var target = $('.replies li.auto-hide');

        target.eq(0).css('display') === 'none' ? target.show('fast') : target.hide('fast'); 
    });


    // 回复某人事件
    $('.answer-say-to').bind('click', function(){
        // 如果是手机端
        if($('.answer-main .ke-container').length == 0){
            $('.answer-main .zx-textarea').val("@" + $(this).data('user_name') + " ");
            $('.answer-main .zx-textarea').focusEnd();
        } else {
            // 滚动到输入框的位置框
            $('html,body').animate({
                scrollTop: $('.answer-main').offset().top + ($.browser.msie ? document.documentElement.scrollTop : 0) - parseInt($('.container_content').css('margin-top')) - 5
            });
            answerEditor.focus();
            answerEditor.html('');
            answerEditor.appendHtml("<span>@" + $(this).data('user_name') + " </span>");
        }
    });
  

    // 修改回答事件
    $('.answer-edit').bind('click', function(){
        $('#edit_answer_modal').modal({'show': true, 'backdrop': 'static'});

        var temp = $(this).parents('li').eq(0).find('.reply-content').html();
        // 如果是手机端
        if($('#edit_answer_modal .ke-container').length == 0){
            // 去掉html标签
            temp = $.ZXUtils.clearHtmlTags(temp);
        } 

        editAnswerEditor.html(temp);

        $('#edit_answer_modal .edit-answer-id').val($(this).data('answer_id'));
    });


    // 修改问题弹出层自动选中问题类型和标签
    if (SElECTED_QUESTION_TYPE){
        // 自动选中问题类型
        $('#div_types input').filter(function(i){
            return $(this).val() == SElECTED_QUESTION_TYPE;
        }).click();

        // 自动选中问题标签
        if(SELECTED_QUESTION_TAGS){
            var tempTags = SELECTED_QUESTION_TAGS.split('-'), 
                tags = {};

            for(var i=0; i<tempTags.length; i++){
                if(tempTags[i]){
                    tags[tempTags[i]] = true;
                }
            }

            $('#div_tags input').filter(function(i){ 
                return tags[$(this).val()]
            }).click();
        }
    }


    // 红心显示隐藏动画
    $('.answer-like-border').bind('mouseenter', function(){
        $(this).find('.answer-like').fadeIn();
        $(this).find('.answer-like-count').fadeOut();
    })
    .bind('mouseleave', function(){
        $(this).find('.answer-like').fadeOut();
        $(this).find('.answer-like-count').fadeIn();
    });


    // 点击赞动作
    $('.answer-like-border').bind('click', function(){
        var me = $(this);
        temp = null;
        postData = {'answer_id': me.data('answer_id')};

        ajaxSend("/question/like_answer", postData, function(data){
            if(data['flag'] != '0'){
                $.ZXMsg.alert('提示', data['result']);
                return;
            }

            // 添加动画
            me.append('<span class="animate-like glyphicon glyphicon-heart"></span>');
            temp = me.find('.animate-like');
            temp.animate({
                opacity: 0.01,
                fontSize: 25,
                top: 11,
                left: 10
            }, 500, function(){
                // 去除动画
                temp.remove();

                // 修改红心为实心
                me.find('.answer-like')
                .removeClass('glyphicon-heart-empty')
                .addClass('glyphicon-heart')
                .css({'color': 'red'});

                // 赞次数+1
                me.find('.answer-like-count')
                .text(parseInt(me.find('.answer-like-count').text()) + 1);
            });
        });
    });

    
    // 问题详情页面 的 问题内容
    if(QUESTION_CONTENT && questionEditor){
        var temp = QUESTION_CONTENT;
        if($('#question_editor .ke-container').length == 0){
            temp = $.ZXUtils.clearHtmlTags(temp);
        }
        questionEditor.html(temp);
    }

    // 问题详情页的回答内容
    if(ANSWER_CONTENT && answerEditor){
        answerEditor.html(ANSWER_CONTENT);
    }

    // 提问页面 的 问题内容
    if(ASK_QUESTION_CONTENT && askEditor){
        askEditor.html(ASK_QUESTION_CONTENT);
    }

    // 验证表单
    $('.ask-question-form').validate({
        errorPlacement: function(error, element) {  
            // 如果是单选按钮将错误信息添加到上上级
            if (element.is(":radio")){
                error.appendTo(element.parent().parent());
            } else {
                error.appendTo(element.parent());
            }
        }
    });

    // 分享事件
    // 分享问题事件
    $('.question-share-qq').bind('click', function(){
        var url = window.location.origin + window.location.pathname,
            title = $(this).parents('.topic').find('.topic-title strong').html();

        $.ZXShare.qq(url, title);
    });
    $('.question-share-sina').bind('click', function(){
        var url = window.location.origin + window.location.pathname,
            title = $(this).parents('.topic').find('.topic-title strong').html();

        $.ZXShare.sinaWeibo(url, title, '');
    });
    // 分享答案事件
    $('.answer-share').toolbar({
        content: '#question-share-tools', 
        position: 'top'
    }, function(target){
        // 点击分享回答按钮保存到全局变量中
        SHARE_ANSWER_ID = target.parents('li').attr('id');
    });
    $('.answer-share-qq').bind('click', function(){
        var url = String.format('{0}%23to_{1}', window.location.origin + window.location.pathname, SHARE_ANSWER_ID),
            title = $(String.format('#{0} .reply-content', SHARE_ANSWER_ID)).html();

        $.ZXShare.qq(url, title);
    });
    $('.answer-share-sina').bind('click', function(){
        var url = String.format('{0}%23to_{1}', window.location.origin + window.location.pathname, SHARE_ANSWER_ID),
            title = $(String.format('#{0} .reply-content', SHARE_ANSWER_ID)).html();

        $.ZXShare.sinaWeibo(url, title, '');
    });

    // 鼠标移动到图片淡入淡出效果
    $('.img-fade-hover').imgFadeHover();

});


function common_remove_question_callback(data) {
    if (data['flag'] == '0') {
        $.ZXMsg.alert('提示', '操作成功!页面即将刷新', 2000);
        window.setTimeout(function(){
            window.location = '/question';
        }, 3000)
        
    } else {
        $.ZXMsg.alert('提示', data['result']);
    }
}

function remove_answer(answer_id){
    $.ZXMsg.confirm('提示', '确认要删除回答吗?', function(result){ 
        if(result){
            var postData = {'answer_id': answer_id};
            g_ajax_processing_obj_id = 'remove_answer_a_id_' + answer_id;
            ajaxSend("/question/remove_answer", postData, common_callback);
        }
    });
}


function remove_question(question_id){
    $.ZXMsg.confirm('提示', '确认要删除此问题吗?', function(result){ 
        if(result){
            var postData = {'question_id': question_id};
            g_ajax_processing_obj_id = 'remove_question_a_id';
            ajaxSend("/question/remove_question", postData, common_remove_question_callback);
        }
    });
}


function set_important(question_id){
    $.ZXMsg.confirm('提示', '确定设置为精华吗?', function(result){ 
        if(result){
            var postData = {'question_id': question_id};
            g_ajax_processing_obj_id = 'set_important_a_id';
            ajaxSend("/question/set_important", postData, common_callback);
        }
    });
}


function cachel_important(question_id){
    $.ZXMsg.confirm('提示', '确定要将此问题取消此精华吗?', function(result){ 
        if(result){
            var postData = {'question_id': question_id};
            g_ajax_processing_obj_id = 'cancel_important_a_id';
            ajaxSend("/question/cachel_important", postData, common_callback);
        }
    });
}


function set_answer_bad(answer_id){
    var postData = {'answer_id': answer_id};
    g_ajax_processing_obj_id = 'set_answer_bad_id_' + answer_id;
    ajaxSend("/question/set_answer_bad", postData, common_callback);
}


function cancel_answer_bad(answer_id){
    var postData = {'answer_id': answer_id};
    g_ajax_processing_obj_id = 'cancel_answer_bad_' + answer_id;
    ajaxSend("/question/cancel_answer_bad", postData, common_callback);
}