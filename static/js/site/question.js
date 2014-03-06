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


    // 初始化自定义的zxCheckbox
    $('#div_tags .zx-checkbox').zxCheckbox();
    $('#div_types .zx-radio').zxRadio();


    // 选择问题类型事件
    $('#div_types .zx-radio>input').bind("change", function(){
        $('#div_tags').hide('fast');

        var type = $(this).val();
        if(!type) {
            return;
        }
        var type_tags = QUESTION_TAGS[type];
        if(!type_tags){
            return;
        }
        $('#div_tags').show('fast').find('label').remove();
        for (var i = type_tags.length - 1; i >= 0; i--) {
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


    // 折叠回答打开关闭事件
    $('.collapse-answer').bind('click', function(){
        var target = $('.replies li.auto-hide');

        target.eq(0).css('display') === 'block' ? target.hide('fast') : target.show('fast'); 
    });


    // 回复某人事件
    $('.answer-say-to').bind('click', function(){
        $('.answer-main .zx-textarea').val("@" + $(this).data('user_name') + " ");
        $('.answer-main .zx-textarea').focusEnd();
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
    var parent = null,
        isRotating = false,
        transformFun = function(target, deg){
            target[0].style.webkitTransform = String.format("rotateY({0}deg)", deg);
            target[0].style.mozTransform = String.format("rotateY({0}deg)", deg);
            target[0].style.msTransform = String.format("rotateY({0}deg)", deg);
            target[0].style.transform = String.format("rotateY({0}deg)", deg);
        },
        animateFun = function(target, isShowHeart){
            // 开始旋转
            jQuery({p: 0}).animate({p: 90}, {
                duration: 300,
                step: function(now, fx) {
                    transformFun(target, now);
                },
                complete: function(){
                    // 旋转到90度后将数字隐藏，将红心显示
                    isShowHeart ? target.find('.answer-like').show() : target.find('.answer-like').hide();
                    isShowHeart ? target.find('.answer-like-count').hide() : target.find('.answer-like-count').show();
                    // 再旋转到0度
                    jQuery({p: 90}).animate({p: 0}, {
                        duration: 300,
                        step: function(now, fx) {
                            transformFun(target, now);
                        }
                    });
                }
            });
        };
    $('.answer-like-border .answer-like-count').bind('mouseenter', function(){
        animateFun($(this).parent(), true);
    });
    $('.answer-like-border .answer-like').bind('mouseleave', function(){
        animateFun($(this).parent(), false);
    });


    // 点击赞动作
    $('.answer-like-border .answer-like').bind('click', function(){
        var parent = $(this).parent(), 
            temp = null,
            postData = {'answer_id': $(this).data('answer_id')};

        ajaxSend("/question/like_answer", postData, function(data){
            if(data['flag'] != '0'){
                alert(data['result']);
                return;
            }

            // 添加动画
            parent.append('<span class="animate-like glyphicon glyphicon-heart"></span>');
            temp = parent.find('.animate-like');
            temp.animate({
                opacity: 0.01,
                fontSize: 25,
                top: 11,
                left: 10
            }, 500, function(){
                // 去除动画
                temp.remove();

                // 修改红心为实心
                parent.find('.answer-like')
                .removeClass('glyphicon-heart-empty')
                .addClass('glyphicon-heart')
                .css({'color': 'red'});

                // 赞次数+1
                parent.find('.answer-like-count')
                .text(parseInt(parent.find('.answer-like-count').text()) + 1);
            });
        });
    });

    
    // 
    UM.getEditor('zx-editor2').setContent(QUESTION_CONTENT);
});