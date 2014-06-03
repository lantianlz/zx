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

    // 根据url 定位到回答位置
    if(window.location.href.indexOf('#to_answer_') > -1){
        $('html,body').animate({
            scrollTop: $('#'+window.location.hash.substring('4')).offset().top + ($.browser.msie ? document.documentElement.scrollTop : 0) - parseInt($('.container_content').css('margin-top')) + 15
        });
    }

    // 初始化自定义的zxCheckbox
    $('#div_tags .zx-checkbox').zxCheckbox();
    $('#div_types .zx-radio').zxRadio();

    // 鼠标移动到图片淡入淡出效果
    setTimeout(function(){$('.img-fade-hover').imgFadeHover();}, 1000);

    // 初始化分享答案事件
    $('.answer-share').toolbar({
        content: '#answer-share-tools', 
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

    // 问题详情页面 的 问题内容
    if(QUESTION_CONTENT && questionEditor){
        var temp = QUESTION_CONTENT;

        // if($('#edit_question_modal .ke-container').length == 0){
        //     temp = $.ZXUtils.clearHtmlTags(temp);
        // }
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

    // 非IE 浏览器添加pin样式
    if(!$.browser.msie){
        $(".pinned").pin({
            containerSelector: ".list-group-item",
            minWidth: 768
        });
    }
    


    // backbone 方式定义事件
    // ================== 问题邀请事件绑定开始 ==================
    var QuestionInviteView = Backbone.View.extend({
        el: '.topic-invite',

        events: {
            'click .search': 'search',
            'click .btn-invite': 'invitePerson'
        },

        // 显示或隐藏邀请框
        toggleInvite: function(){
            var target = this.$el;
        
            target.css('display') === 'block' ? target.hide() : target.show();
        },

        // 查询邀请人
        search: function(){
            // todo
            $.ZXMsg.alert('查询某人', this.$('.search-input').val());
        },

        // 邀请某人回答问题
        invitePerson: function(){
            // todo
            $.ZXMsg.alert('邀请某人', this.$('.btn-invite').data('user_id'));
        }
    });
    var questionInviteView = new QuestionInviteView();
    // ================== 问题邀请事件绑定开始 ==================

    // ================== 问题事件绑定开始 =====================
    var QuestionView = Backbone.View.extend({  
        el: '.topic-footer',

        events: {  
            'click .question-share-qq': 'shareQQ',
            'click .question-share-sina': 'shareSina',
            'click .set-important': 'setImportant',
            'click .cancel-important': 'cancelImportant',
            'click .remove-question': 'removeQuestion',
            'click .invite': 'invite',
        },

        // 分享问题到QQ
        shareQQ: function(){
            var url = window.location.origin + window.location.pathname,
                title = this.$('.question-share-qq').parents('.topic').find('.topic-title strong').html();

            $.ZXShare.qq(url, title);
        },

        // 分享问题到sina
        shareSina: function(){
            var url = window.location.origin + window.location.pathname,
                title = this.$('.question-share-sina').parents('.topic').find('.topic-title strong').html();

            $.ZXShare.sinaWeibo(url, title, '');
        },

        // 设置精华
        setImportant: function(){
            var questionId = this.$el.data('question_id');

            $.ZXMsg.confirm('提示', '确定将此问题设置为精华吗?', function(result){ 
                if(result){
                    // 设置ajax元素id,防止多次点击
                    g_ajax_processing_obj_id = this.$('.set-important').setUUID().attr('id');

                    ajaxSend("/question/set_important", {'question_id': questionId}, common_callback);
                }
            });
        },

        // 取消设置精华
        cancelImportant: function(){
            var questionId = this.$el.data('question_id');

            $.ZXMsg.confirm('提示', '确定要取消精华吗?', function(result){ 
                if(result){
                    // 设置ajax元素id,防止多次点击
                    g_ajax_processing_obj_id = this.$('.cancel-important').setUUID().attr('id');

                    ajaxSend("/question/cancel_important", {'question_id': questionId}, common_callback);
                }
            });
        },

        // 删除问题
        removeQuestion: function(){
            var questionId = this.$el.data('question_id');

            $.ZXMsg.confirm('提示', '确认要删除此问题吗?', function(result){ 
                if(result){
                    // 设置ajax元素id,防止多次点击
                    g_ajax_processing_obj_id = this.$('.remove-question').setUUID().attr('id');

                    ajaxSend(
                        "/question/remove_question", 
                        {'question_id': questionId},
                        function(data){
                            if (data['errcode'] == '0') {
                                $.ZXMsg.alert('提示', '操作成功!页面即将刷新', 2000);
                                window.setTimeout(function(){
                                    window.location = '/question';
                                }, 3000)
                                
                            } else {
                                $.ZXMsg.alert('提示', data['errmsg']);
                            }
                        } 
                    );

                }
            });
        },

        // 邀请框打开关闭事件
        invite: function(){
            questionInviteView.toggleInvite();
        }

    });  
    new QuestionView();
    // ================== 问题事件绑定结束 ========================

    // ================== 问题各个回答事件绑定开始 ==================
    var QuestionAnswerView = Backbone.View.extend({
        el: '.list-group-item',

        events: {
            'click .answer-share': 'shareAnswer',
            'click .answer-collapse': 'collapseAnswer',
            'click .answer-say-to': 'sayTo',
            'click .answer-no-help': 'noHelp',
            'click .answer-cancel-no-help': 'cancelNoHelp',
            'click .answer-edit': 'editAnswer',
            'click .answer-remove': 'removeAnswer',
            'click .answer-like-border': 'likeAnswer',
            'click .liked-persons .get-more': 'getMoreLikedPersons',
            'click .like': 'like',
            'mouseenter': 'showAnswerTools',
            'mouseleave': 'hideAnswerTools',
            'mouseenter .answer-like-border': 'showHeart',
            'mouseleave .answer-like-border': 'hideHeart'
        },

        like: function(sender){
            var target = $(sender.currentTarget),
                me = this;

            // 操作成功执行动画
            // target
            // .children()
            // .addClass('light');

            // target.find('img').addClass('light-img');

            // target.find('.answer-like-count')
            // .text(parseInt(target.find('.answer-like-count').text()) + 1);

            
            ajaxSend(
                "/question/like_answer", 
                {'answer_id': $(target).data('answer_id')}, 
                function(data){
                    if(data['errcode'] != '0'){
                        $.ZXMsg.alert('提示', data['errmsg']);
                        return;
                    }

                    // 操作成功执行动画
                    target
                    .children()
                    .addClass('light');

                    target.find('img').addClass('light-img');

                    target.find('.answer-like-count')
                    .text(parseInt(target.find('.answer-like-count').text()) + 1);
                }
            );
            
            
        },

        // 赞动画
        _likeAnswerAnimate: function(target){
            
            target.append('<span class="animate-like glyphicon glyphicon-heart"></span>');

            var temp = target.find('.animate-like');
            temp.animate({
                opacity: 0.01,
                fontSize: 25,
                top: 11,
                left: 10
            }, 500, function(){
                // 去除动画
                temp.remove();

                // 修改红心为实心
                target.find('.answer-like')
                .removeClass('glyphicon-heart-empty')
                .addClass('glyphicon-heart')
                .css({'color': 'red'});

                // 赞次数+1
                target.find('.answer-like-count')
                .text(parseInt(target.find('.answer-like-count').text()) + 1);
            });
        },

        // 显示红心
        showHeart: function(sender){
            var target = $(sender.currentTarget);

            target.find('.answer-like').fadeIn();
            target.find('.answer-like-count').fadeOut();
        },

        // 隐藏红心
        hideHeart: function(sender){
            var target = $(sender.currentTarget);
            
            target.find('.answer-like').fadeOut();
            target.find('.answer-like-count').fadeIn();
        },

        // 赞回答
        likeAnswer: function(sender){
            var target = $(sender.currentTarget),
                view = this;

            ajaxSend(
                "/question/like_answer", 
                {'answer_id': $(sender.delegateTarget).data('answer_id')}, 
                function(data){
                    if(data['errcode'] != '0'){
                        $.ZXMsg.alert('提示', data['errmsg']);
                        return;
                    }

                    // 操作成功执行动画
                    view._likeAnswerAnimate(target);
                }
            );
        },

        // 分享回答操作
        shareAnswer: function(){
        },

        // 显示与折叠答案
        collapseAnswer: function(){
            var target = this.$el.parent().find('li.auto-hide');

            target.eq(0).css('display') === 'none' ? target.show('fast') : target.hide('fast');
        },

        // 回复某人
        sayTo: function(sender){
            var target = $(sender.currentTarget);

            // 如果是手机端
            if($('.answer-main .ke-container').length == 0){
                $('.answer-main .zx-textarea').val("@" + target.data('user_name') + " ");
                $('.answer-main .zx-textarea').focusEnd();
            } else {
                // 滚动到输入框的位置框
                $('html,body').animate({
                    scrollTop: $('.answer-main').offset().top 
                        + ($.browser.msie ? document.documentElement.scrollTop : 0) 
                        - parseInt($('.container_content').css('margin-top')) 
                        - 5
                });
                answerEditor.focus();
                answerEditor.html('');
                answerEditor.appendHtml("<span>@" + target.data('user_name') + " </span>");
            }
        },

        // 设置回答没有帮助
        noHelp: function(sender){
            var target = $(sender.currentTarget);

            // 设置ajax元素id,防止多次点击
            g_ajax_processing_obj_id = target.setUUID().attr('id');

            ajaxSend(
                "/question/set_answer_bad", 
                {'answer_id': $(sender.delegateTarget).data('answer_id')}, 
                common_callback
            );
        },

        // 取消回答没有帮助
        cancelNoHelp: function(sender){
            var target = $(sender.currentTarget);

            // 设置ajax元素id,防止多次点击
            g_ajax_processing_obj_id = target.setUUID().attr('id');

            ajaxSend(
                "/question/cancel_answer_bad", 
                {'answer_id': $(sender.delegateTarget).data('answer_id')}, 
                common_callback
            );
        },

        // 编辑回答
        editAnswer: function(sender){
            var target = $(sender.currentTarget);

            // 显示弹出框
            $('#edit_answer_modal').modal({'show': true, 'backdrop': 'static'});

            var content = target.parents('li').eq(0).find('.reply-content').html();
            // 如果是手机端
            if($('#edit_answer_modal .ke-container').length == 0){
                // 去掉html标签
                content = $.ZXUtils.clearHtmlTags(content);
            } 

            editAnswerEditor.html(content);

            $('#edit_answer_modal .edit-answer-id').val($(sender.delegateTarget).data('answer_id'));

        },

        // 删除回答
        removeAnswer: function(sender){
            $.ZXMsg.confirm('提示', '确认要删除回答吗?', function(result){ 
                if(result){
                    var target = $(sender.currentTarget);

                    // 设置ajax元素id,防止多次点击
                    g_ajax_processing_obj_id = target.setUUID().attr('id');

                    ajaxSend(
                        "/question/remove_answer", 
                        {'answer_id': $(sender.delegateTarget).data('answer_id')}, 
                        common_callback
                    );
                }
            });
        },

        // 获取所有点赞的人
        getMoreLikedPersons: function(sender){
            var target = $(sender.currentTarget),
                template = '<a class="gray-gray zx-cardtips" href="/p/{0}" class="zx-cardtips" data-user_id="{1}">{2}</a>'
                answerId = target.data('answer_id');

            // 设置ajax元素id,防止多次点击
            g_ajax_processing_obj_id = target.setUUID().attr('id');

            ajaxSend(
                "/question/get_answer_like", 
                {'answer_id': answerId}, 
                function(data){
                    target.parent().html(
                        _.map(data, function(p){
                            return String.format(template, p.user_id, p.user_id, p.user_nick)
                        }).join('、') + '  为Ta亮灯'
                    )
                    // 注册名片事件
                    $.ZXTooltipster.PersonCard();
                }
            );
        },

        // 显示回答工具条
        showAnswerTools: function(sender){
            $(sender.delegateTarget).find('.reply-tools .auto-hide').show();
        },

        // 隐藏回答工具条
        hideAnswerTools: function(sender){
            $(sender.delegateTarget).find('.reply-tools .auto-hide').hide();
        }
    });
    new QuestionAnswerView();
    // ================== 问题各个回答事件绑定结束 ==================
});
