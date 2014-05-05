/*
    为字符串拓展format方法
    用例：
    String.format('{0}, {1}!', 'Hello', 'world');
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
        return '0' + temp;
    } else {
        return data;
    }
}


/*
    拓展Jquery方法 
*/
(function(){
    /*
        设置文本框光标位置
        selectionStart: 光标开始位置
        selectionEnd: 光标结束位置

        用例:
        $('#selector').setSelection(0, 1);
    */
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
    };

    /*
        设置文本框光标位置到最后

        用例:
        $('#selector').focusEnd();
    */
    $.fn.focusEnd = function() {
        return this.setSelection(this.val().length, this.val().length);
    };

    // 自定义checkbox
    $.fn.zxCheckbox = function(){

        this.find('input').live('change', function(){
            var parent = $(this).parent();
            
            parent.hasClass('checked') ? parent.removeClass('checked') : parent.addClass('checked');
        });

        return this;
    };

    // 自定义radio
    $.fn.zxRadio = function(){

        this.find('input').live('change', function(){
            
            $('input[name='+$(this).attr('name')+']').each(function(){
                var me = $(this), parent = me.parent();
                
                me.attr('checked') ? parent.addClass('checked') : parent.removeClass('checked');
            });
            
        });

        return this;
    };


    /*
        鼠标移动渐变换图片插件，效果参见第三方登录图标
        
        用例:
        $('.img-fade-hover').imgFadeHover();

        dom如下, 需要指定鼠标移上去显示的图片地址data-change_img:
        <img class="avatar-20 img-fade-hover" 
            data-change_img="{{MEDIA_URL}}img/common/qq-active.png" 
            src="{{MEDIA_URL}}img/common/qq.png">
    */
    $.fn.imgFadeHover = function(){
        var changeFun = function(target, temp){
            // IE 只能设置filter属性
            if($.browser.msie){
                // target[0].filter = String.format("'alpha(opacity={0})'", Math.round(temp));
                target[0].filter = String.format("' progid:DXImageTransform.Microsoft.Alpha(Opacity={0})'", Math.round(temp));
            } else {
                target.css('opacity', temp/100);
            }
        };

        return this.each(function(){
            $(this).bind('mouseenter', function(){
                var me = $(this),
                    originImg = me.attr('src'),
                    changeImg = me.data('change_img');

                // me.data('change_img', originImg);
                // me.attr('src', changeImg);
                // me.css({'opacity': '0'}).animate({'opacity': '0.99'}, 300)
                        
                // 兼容IE的蛋疼png透明问题写法
                me.data('change_img', originImg);
                me.attr('src', changeImg);
                
                jQuery({p: 0}).animate({p: 99}, {
                    duration: 300,
                    step: function(now, fx) {
                        changeFun(me, now);
                    }
                });
            })
            .bind('mouseleave', function(){
                var me = $(this),
                    originImg = me.data('change_img'),
                    changeImg = me.attr('src');
                
                // me.data('change_img', changeImg);
                // me.attr('src', originImg);
                // me.css({'opacity': '0'}).animate({'opacity': '0.99'}, 300);

                // 兼容IE的蛋疼png透明问题写法
                me.data('change_img', changeImg);
                me.attr('src', originImg);
                
                jQuery({p: 0}).animate({p: 99}, {
                    duration: 300,
                    step: function(now, fx) {
                        changeFun(me, now);
                    }
                });

            });
        });

        
    };


    /*
        给指定元素生成一个唯一id, 主要使用场景ajax需要一个id，防止多次点击

        用例：
        $('.someclass').setUUID();
    */
    $.fn.setUUID = function(){
        return this.each(function(){
            return $(this).attr('id', new Date().getTime());
        });
    }




    /*
        工具包
    */
    $.ZXUtils = {
        version: '1.0.0',
        author: 'stranger',
        description: '工具包'
    };
    /*
        去掉所有的html标签
        target: 要操作的字符串

        用例:
        $.ZXUtils.clearHtmlTags('<div>1</div>');
    */
    $.ZXUtils.clearHtmlTags = function(target){
        if(!target){
            return '';
        }
        return target.replace(/<[^>].*?>/g,"");
    };

    /*
        去掉所有的转义字符
        target: 要操作的字符串

        用例:
        $.ZXUtils.clearEscapeCharacters('<div>1</div>');
    */
    $.ZXUtils.clearEscapeCharacters = function(target){
        if(!target){
            return '';
        }
        return target.replace(/&[^;].*?;/g, '');
    };

    /*
        屏幕宽度小于 768 归于手机
    */
    $.ZXUtils.isPhone = function(){
        return ($(window).width() < 768) ? true : false;
    };

    /*
        屏幕宽度 大于768 而 小于992 归于平板
    */
    $.ZXUtils.isPad = function(){
        return (768 <= $(window).width() && $(window).width() < 992) ? true : false;
    };

    /*
        屏幕宽度大于 992 归于桌面
    */
    $.ZXUtils.isDesktop = function(){
        return (992 <= $(window).width()) ? true : false;
    };


    /* 
        弹窗插件
    */
    $.ZXMsg = {
        version: '1.0.0',
        author: 'stranger',
        description: '取代浏览器自带的消息框'
    };
    /*
        通用alert框
        alertTitle: 弹出框的标题
        alertMsg: 弹出框的描述
        delayCloseSeconds: 延迟几秒之后自动关闭

        用例:
        $.ZXMsg.alert('提示', '操作成功!');
        $.ZXMsg.alert('提示', '操作成功, 5秒后自动关闭!', 5000);
    */
    $.ZXMsg.alert = function(alertTitle, alertMsg, delayCloseSeconds){
        var alertHtml = [
            '<div class="modal fade" id="alert_modal" tabindex="-1" role="dialog">',
                '<div class="modal-dialog w400">',
                    '<div class="modal-content">',
                        '<div class="modal-header pb-5">',
                            '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>',
                            '<h4 class="modal-title">'+alertTitle+'</h4>',
                        '</div>',
                        '<div class="modal-body">',
                            alertMsg,
                        '</div>',
                    '</div>',
                '</div>',
            '</div>'
        ].join('');

        // 将alert框添加进body
        $('body').append(alertHtml);
        
        // 关闭之后清除掉自己
        $('#alert_modal').on('hidden.bs.modal', function (e) {
            $(this).remove();
        });

        // 显示alert框
        $('#alert_modal').modal('show');

        // 是否设置了自动关闭
        if(delayCloseSeconds){
            window.setTimeout(function(){
                if($('#alert_modal').length > 0){
                    $('#alert_modal').modal('hide');
                }
                
            }, delayCloseSeconds)
        }
    };

    /*
        通用confirm框
        confirmTitle: 弹出框的标题
        confirmMsg: 弹出框的描述
        callback: 回调函数

        用例:
        $.ZXMsg.confirm('提示', '确认要删除?', function(result){ //to do...});
    */
    $.ZXMsg.confirm = function(confirmTitle, confirmMsg, callback){
        var confirmHtml = [
            '<div class="modal fade" id="confirm_modal" tabindex="-1" role="dialog">',
                '<div class="modal-dialog w400">',
                    '<div class="modal-content">',
                        '<div class="modal-header pb-5">',
                            '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>',
                            '<h4 class="modal-title">'+confirmTitle+'</h4>',
                        '</div>',
                        '<div class="modal-body">',
                            confirmMsg,
                        '</div>',
                        '<div class="modal-footer">',
                            '<button type="button" class="btn btn-default confirm-cancel">取消</button>',
                            '<button type="button" class="btn btn-primary confirm-ok">确定</button>',
                        '</div>',
                    '</div>',
                '</div>',
            '</div>'
        ].join('');


        // 将confirm框添加进body
        $('body').append(confirmHtml);
        
        // 确定事件
        $('#confirm_modal .confirm-ok').bind('click', function(){
            if(callback){
                callback(true);
            }

            $('#confirm_modal').modal('hide');
        });

        // 取消事件
        $('#confirm_modal .confirm-cancel').bind('click', function(){
            if(callback){
                callback(false);
            }

            $('#confirm_modal').modal('hide');
        });

        // 关闭之后清除掉自己
        $('#confirm_modal').on('hidden.bs.modal', function (e) {
            $(this).remove();
        });

        // 显示confirm框
        $('#confirm_modal').modal({'show': true, 'backdrop': 'static'});

    };


    /*
        私信方法
        userId: 用户id
        userName: 用户名称

        用例：
        $.ZXMsg.sendPrivateMsg('1', '半夜没事瞎溜达');
    */
    $.ZXMsg.sendPrivateMsg = function(userId, userName){
        var postUrl = '/',
            privateMsgHtml = [
                '<div class="modal fade" id="private_message_modal" role="dialog">',
                    '<div class="modal-dialog w400">',
                        '<div class="modal-content">',
                            '<form role="form" class="form-horizontal" method="post" action="">',
                                '<div class="modal-header">',
                                    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>',
                                    '<h4 class="modal-title">发送私信</h4>',
                                '</div>',
                                '<div class="modal-body pb-0">',
                                    '<div class="form-group">',
                                        '<label class="col-xs-3 control-label">发送给</label>',
                                        '<div class="col-xs-9">',
                                            '<label id="receiver_label" class="control-label"></label>',
                                            '<input type="hidden" name="receiver">',
                                        '</div>',
                                    '</div>',
                                    '<div class="form-group">',
                                        '<label class="col-xs-3 control-label">消息</label>',
                                        '<div class="col-xs-9">',
                                            '<textarea rows="4" name="message" class="form-control" placeholder="请输入消息内容" value=""></textarea>',
                                        '</div>',
                                    '</div>',
                                '</div>',
                                '<div class="modal-footer">',
                                    '<button type="button" class="btn btn-default" data-dismiss="modal">关 闭</button>',
                                    '<button type="button" class="btn btn-primary send">发 送</button>',
                                '</div>',
                            '</form>',
                        '</div>',
                    '</div>',
                '</div>'
            ].join('');

        
        // 是否第一次创建私信框
        if($('#private_message_modal').length == 0){
            // 将私信框添加进body
            $('body').append(privateMsgHtml);

            // 绑定发送事件
            $('#private_message_modal .send').bind('click', function(){
                // todo ...
                $('#private_message_modal').modal('hide');

                $.ZXMsg.alert('提示', '给 <strong>'+userName+'</strong> 的私信发送成功!', 3000);
            });
        }

        // 设置值
        $('#private_message_modal input[name=receiver]').val(userId);
        $('#private_message_modal #receiver_label').html(userName);

        // 显示
        $('#private_message_modal').modal({'show': true, 'backdrop': 'static'});

    };


    /*
        意见反馈方法

        用例：
        $.ZXMsg.feedback();
    */
    $.ZXMsg.feedback = function(){
        var postUrl = '/',
            privateMsgHtml = [
                '<div class="modal fade" id="feedback_modal" role="dialog">',
                    '<div class="modal-dialog w400">',
                        '<div class="modal-content">',
                            '<form role="form" class="form-horizontal" method="post" action="">',
                                '<div class="modal-header">',
                                    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>',
                                    '<h4 class="modal-title">意见反馈</h4>',
                                '</div>',
                                '<div class="modal-body pb-0">',
                                    '<div class="form-group">',
                                        '<label class="col-sm-12">填写你对智选的意见或建议:</label>',
                                    '</div>',
                                    '<div class="form-group">',
                                        '<div class="col-sm-12">',
                                            '<textarea rows="4" name="feedback_message" class="form-control" placeholder="你的期望、使用感受、任何想法都行" value=""></textarea>',
                                        '</div>',
                                    '</div>',
                                '</div>',
                                '<div class="modal-footer">',
                                    '<button type="button" class="btn btn-default" data-dismiss="modal">关 闭</button>',
                                    '<button type="button" class="btn btn-primary send">提 交</button>',
                                '</div>',
                            '</form>',
                        '</div>',
                    '</div>',
                '</div>'
            ].join('');

        
        // 是否第一次创建反馈框
        if($('#feedback_modal').length == 0){
            // 将反馈框添加进body
            $('body').append(privateMsgHtml);

            // 绑定发送事件
            $('#feedback_modal .send').bind('click', function(){
                // todo ...
                $('#feedback_modal').modal('hide');

                $.ZXMsg.alert('提示', '我们会仔细阅读你的反馈，非常感谢你对智选的关注!', 3000);
            })
        }

        // 显示
        $('#feedback_modal').modal({'show': true, 'backdrop': 'static'});

    };


    // 分享插件
    $.ZXShare = {
        version: '1.0.0',
        author: 'stranger',
        description: '分享插件'
    };
    /*
        分享到微博
        url: 要分享的url
        title: 要分享的描述
        pic: 图片地址
        notOpenWin: 是否要弹出窗口
        
        用例：
        $.ZXShare.sinaWeibo('www.a.com', 'test', '1.jpg', true);
    */
    $.ZXShare.sinaWeibo = function(url, title, pic, notOpenWin){
        var clearTitle = $.ZXUtils.clearEscapeCharacters($.ZXUtils.clearHtmlTags(title)),
            sinaUrl = String.format(
                "http://service.weibo.com/share/share.php?url={0}&title={1}&pic={2}&appkey={3}&ralateUid={4}&searchPic=false",
                url,
                (clearTitle.length >= 110) ? (clearTitle.substring(0, 110) + '...') : clearTitle,
                pic ? pic : '',
                '266639437',
                '5083374708'
            );

        notOpenWin = notOpenWin ? notOpenWin : false;
        if(!notOpenWin){
            window.open(sinaUrl, '_blank');
        }

        return sinaUrl;
    };

    /*
        分享到qq
        url: 要分享的url
        title: 要分享的描述
        desc: 要分享的描述
        notOpenWin: 是否要弹出窗口

        用例：
        $.ZXShare.qq('www.a.com', 'test', 'test', true);
    */
    $.ZXShare.qq = function(url, title, desc, notOpenWin){
        var clearTitle = $.ZXUtils.clearEscapeCharacters($.ZXUtils.clearHtmlTags(title)),
            clearDesc = $.ZXUtils.clearEscapeCharacters($.ZXUtils.clearHtmlTags(desc)),
            qqUrl = String.format(
                "http://connect.qq.com/widget/shareqq/index.html?url={0}&title={1}&desc={2}&source={3}",
                url,
                (clearTitle.length >= 110) ? (clearTitle.substring(0, 110) + '...') : clearTitle,
                clearDesc ? clearDesc : '在智选上看到点好东西, 推荐你看看',
                'shareqq'
            );

        notOpenWin = notOpenWin ? notOpenWin : false;

        if(!notOpenWin){
            window.open(qqUrl, '_blank');
        } 

        return qqUrl;
    };


    /*
        业务操作
    */
    $.ZXOperation = {
        version: '1.0.0',
        author: 'stranger',
        description: '业务操作'
    };
    /*
        关注用户
        userId: 用户id
        callback: 回调函数

        用例：
        $.ZXOperation.followPeople('1', function(){alert('1')})
    */
    $.ZXOperation.followPeople = function(userId, callback){
        ajaxSend("/timeline/follow/" + userId, {}, callback, 'GET');
    };

    /*
        取消关注用户
        userId: 用户id
        callback: 回调函数

        用例：
        $.ZXOperation.unfollowPeople('1', function(){alert('1')})
    */
    $.ZXOperation.unfollowPeople = function(userId, callback){
        ajaxSend("/timeline/unfollow/" + userId, {}, callback, 'GET');
    };

    /*
        关注话题
        topicId: 话题id
        callback: 回调函数

        用例：
        $.ZXOperation.followTopic('1', function(){alert('1')})
    */
    $.ZXOperation.followTopic = function(topicId, callback){
        
    };

    /*
        取消关注话题
        topicId: 话题id
        callback: 回调函数

        用例：
        $.ZXOperation.unfollowTopic('1', function(){alert('1')})
    */
    $.ZXOperation.unfollowTopic = function(topicId, callback){
        
    };


    /*
        名片操作
    */
    $.ZXTooltipster = {
        version: '1.0.0',
        author: 'stranger',
        description: '名片操作'
    };
    /*
        用户名片
        自动将class为 zx-cardtips 的元素注册弹出名片
        需要设置 data-user_id 属性为用户id

        用例:
        $.ZXTooltipster.PersonCard();
    */
    $.ZXTooltipster.PersonCard = function(){
        var cardtipsHtml = [
            '<div class="cardtips f12">',
                '<div class="profile row f14">',
                    '<div class="col-md-3">',
                        '<img class="avatar avatar-55 avatar-circle ml-10 mt-5" src="{0}" >',
                    '</div>',
                    '<div class="col-md-9">',
                        '<div class="pt-10 pb-5"><a href="/p/{10}">{1}</a>{12}</div>',
                        '<div class="pt-5">',
                            '<span>提问<a href="#" class="pl-3 pr-15">{2}</a></span>',
                            '<span>回答<a href="#" class="pl-3 pr-15">{3}</a></span>',
                            '<span>赞<a href="#" class="pl-3 pr-15">{4}</a></span>',
                        '</div>',
                    '</div>',
                '</div>',
                '<div class="desc pl-10 pt-5 w300 co6">{5}</div>',
                '<div class="topics pl-10 pt-10 pb-5 w300 co6 none">擅长话题: {11}</div>',
                '<div class="tools top-border bdc-eee pt-5 mt-5" data-user_name="{6}" data-user_id="{7}">',
                    '<a class="send-message pr-10 pt-5 pl-5 none" href="javascript: void(0)">',
                        '<span class="glyphicon glyphicon-envelope"></span> 私信ta',
                    '</a>',
                    '<button type="button" class="btn btn-primary btn-xs follow ml-10 mr-5 pull-right {8}">关注ta</button>',
                    '<button type="button" class="btn btn-default btn-xs unfollow mr-5 pull-right {9}">取消关注</button>',
                '</div>',
            '</div>'
        ].join('');

        // 手机访问不要设置弹出名片
        if($.ZXUtils.isPhone()){
            return;
        }

        // 设置插件
        $('.zx-cardtips').tooltipster({
            animation: 'swing',
            delay: 150,
            trigger: 'hover',
            theme: 'tooltipster-shadow',
            interactive: true,
            interactiveTolerance: 300,
            speed: 350,
            updateAnimation: false,
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
                            if(data.flag=='0'){
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
                                    data.is_follow?'':'hide', //取消关注按钮
                                    data.id,
                                    // 拼装话题
                                    $(data.topics).map(function(){
                                        return  String.format(
                                            '<a class="border-block-blue ml-5 pl-5 pr-5" href="question/topic/{0}">{1}</a>', 
                                            this['topic_id'], 
                                            this['topic_name']
                                        )
                                    }).get().join(''),
                                    data.gender == '1' ? ('<img class="w15 mt--2" src="'+MEDIA_URL+'img/common/male.png" title="男" />') : ('<img class="w15 mt--2" src="'+MEDIA_URL+'img/common/female.png" title="女" />')
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
        $('.cardtips .send-message').live('click', function(){
            var target = $(this).parents('.tools').eq(0);
            $.ZXMsg.sendPrivateMsg(target.data('user_id'), target.data('user_name'));
        });
        // 关注事件
        $('.cardtips .follow').live('click', function(){
            var target = $(this).parents('.tools').eq(0);
            $.ZXMsg.alert('关注人', target.data('user_id') + target.data('user_name'));
        });
        // 取消关注事件
        $('.cardtips .unfollow').live('click', function(){
            var target = $(this).parents('.tools').eq(0);
            $.ZXMsg.alert('取消关注', target.data('user_id') + target.data('user_name'));
        });
        
    };

    /*
        话题名片
        自动将class为 zx-topictips 的元素注册弹出名片
        需要设置 data-topic_id 属性为话题id

        用例:
        $.ZXTooltipster.PersonCard();
    */
    $.ZXTooltipster.TopicCard = function(){
        // 弹出话题名片设置
        var topictipsHtml = [
            '<div class="topictips f12">',
                '<div class="profile row f14">',
                    '<div class="col-md-3">',
                        '<img class="avatar avatar-55 avatar-circle ml-10 mt-5" src="{0}" >',
                    '</div>',
                    '<div class="col-md-9">',
                        '<div class="pt-10 pb-5"><a href="/question/topic/1">{1}</a></div>',
                        '<div class="question-info pt-5">',
                            '<span>关注者<span class="pl-3 pr-15 fb">{2}</span></span>',
                            '<span>提问<span class="pl-3 pr-15 fb">{3}</span></span>',
                        '</div>',
                    '</div>',
                '</div>',
                '<div class="desc pl-10 pt-5 w300 co6">{4}</div>',
                '<div class="tools top-border bdc-eee pt-5 mt-5 text-right" data-topic_id="{7}">',
                    '<button type="button" class="btn btn-primary btn-xs follow mr-5 ml-10 {5}">关注ta</button>',
                    '<button type="button" class="btn btn-default btn-xs unfollow mr-5 {6}">取消关注</button>',
                '</div>',
            '</div>'
        ].join('');

        // 手机访问不要设置弹出名片
        if($.ZXUtils.isPhone()){
            return;
        }

        // 设置插件
        $('.zx-topictips').tooltipster({
            animation: 'swing',
            delay: 200,
            trigger: 'hover',
            theme: 'tooltipster-shadow',
            interactive: true,
            interactiveTolerance: 300,
            autoClose: true,
            //content: topictipsHtml,
            updateAnimation: false,
            contentAsHTML: true,
            content: '信息加载中...',
            functionBefore: function(origin, continueTooltip) {

                // we'll make this function asynchronous and allow the tooltip to go ahead and show the loading notification while fetching our data
                continueTooltip();
                
                // next, we want to check if our data has already been cached
                if (origin.data('ajax') !== 'cached') {
                    $.ajax({
                        type: 'POST',
                        dataType: 'json',
                        url: '/question/get_topic_info_by_id?topic_id=' + origin.data('topic_id'),
                        success: function(data) {
                            if(data.flag=='0'){
                                origin.tooltipster('content', String.format(
                                    topictipsHtml, 
                                    data.avatar,
                                    data.name, 
                                    data.follow_count,
                                    data.question_count,
                                    data.desc,
                                    data.is_follow?'hide':'', // 关注按钮
                                    data.is_follow?'':'hide', //取消关注按钮
                                    data.id
                                )).data('ajax', 'cached');
                            } else {
                                origin.tooltipster('content', '加载名片失败');
                            }
                        }
                    });
                }
            }
        });
        // 关注事件
        $('.topictips .follow').live('click', function(){
            var target = $(this).parents('.tools').eq(0);
            $.ZXMsg.alert('关注话题', target.data('topic_id'));
        });
        // 取消关注事件
        $('.topictips .unfollow').live('click', function(){
            var target = $(this).parents('.tools').eq(0);
            $.ZXMsg.alert('取消关注话题', target.data('topic_id'));
        });
    };


})(jQuery);


/*
    创建 KindEditor 编辑器
    selector: textarea的选择器
*/
function createEditor(selector){
    // 如果是手机端则直接使用html的textarea
    if($.ZXUtils.isPhone()){
        return $(selector);
    } else {
        return KindEditor.create(selector, {
            resizeType : 1,
            width: '100%',
            //autoHeightMode : true,
            allowPreviewEmoticons : false,
            allowImageUpload : true,
            allowImageRemote: true,
            // basePath: '/',
            uploadJson: '/save_img',
            pasteType : 1,
            cssData: 'body{font-family: "Helvetica Neue",Helvetica,"Lucida Grande","Luxi Sans",Arial,"Hiragino Sans GB",STHeiti,"Microsoft YaHei","Wenquanyi Micro Hei","WenQuanYi Micro Hei Mono","WenQuanYi Zen Hei","WenQuanYi Zen Hei Mono",LiGothicMed; font-size: 14px; color: #222;}',
            themesPath: MEDIA_URL + "css/kindeditor/themes/",
            pluginsPath: MEDIA_URL + "js/kindeditor/plugins/",
            langPath: MEDIA_URL + "js/kindeditor/",
            items : [
                'bold', 'italic', 'underline', 'removeformat', '|', 
                'justifyleft', 'justifycenter', 'justifyright', 'insertorderedlist', 'insertunorderedlist', '|', 
                'image', 'link', '|', 
                'fullscreen'
            ],
            afterCreate : function() { 
                //this.loadPlugin('autoheight');
                this.sync(); 
            }, 
            afterBlur:function(){ 
                this.sync(); 
            },
            afterUpload : function(url) {
            }
        });
    }

    
}

/*
    jQuery.validate 中文提示
*/
jQuery.extend(jQuery.validator.messages, {
    required: "必填字段",
    remote: "请修正该字段",
    email: "请输入正确格式的电子邮件",
    url: "请输入合法的网址",
    date: "请输入合法的日期",
    dateISO: "请输入合法的日期 (ISO).",
    number: "请输入合法的数字",
    digits: "只能输入整数",
    creditcard: "请输入合法的信用卡号",
    equalTo: "请再次输入相同的值",
    accept: "请输入拥有合法后缀名的字符串",
    maxlength: jQuery.validator.format("请输入一个 长度最多是 {0} 的字符串"),
    minlength: jQuery.validator.format("请输入一个 长度最少是 {0} 的字符串"),
    rangelength: jQuery.validator.format("请输入 一个长度介于 {0} 和 {1} 之间的字符串"),
    range: jQuery.validator.format("请输入一个介于 {0} 和 {1} 之间的值"),
    max: jQuery.validator.format("请输入一个最大为{0} 的值"),
    min: jQuery.validator.format("请输入一个最小为{0} 的值")
});


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
    $('.zx-tooltip').tooltip('hide');
    
    // 初始化名片
    $.ZXTooltipster.PersonCard();
    $.ZXTooltipster.TopicCard();


    // 鼠标移动到导航条登录用户名时自动弹出下拉框
    var dropdownTimeout = null,
        showDropdown = function(target){
            $(target).addClass('open');

            // if(dropdownTimeout){
            //     window.clearTimeout(dropdownTimeout);
            //     dropdownTimeout = null;
            // }
        },
        hideDropdown = function(target){
            //if(!dropdownTimeout){
                //dropdownTimeout = window.setTimeout(function(){
                    $(target).removeClass('open');
                    //dropdownTimeout = null;
                //}, 1)
            //}
        };
    
    $('.user-menu .dropdown-toggle')
    .bind('mouseenter', function(){showDropdown('.user-menu')})
    .bind('mouseleave', function(){hideDropdown('.user-menu')});

    $('.user-menu .dropdown-menu')
    .bind('mouseenter', function(){showDropdown('.user-menu')})
    .bind('mouseleave', function(){hideDropdown('.user-menu')});

    $('.user-notice .dropdown-toggle')
    .bind('mouseenter', function(){showDropdown('.user-notice')})
    .bind('mouseleave', function(){hideDropdown('.user-notice')});

    $('.user-notice .dropdown-menu')
    .bind('mouseenter', function(){showDropdown('.user-notice')})
    .bind('mouseleave', function(){hideDropdown('.user-notice')});


    // 隐藏所有 auto-hide 样式
    $('.auto-hide').hide();

    
    // 用户反馈
    $('.follow-zx .feedback').bind('click', function(){
        $.ZXMsg.feedback();
    });
});

