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

    // 选择问题类型事件
    $('#sel_question_type').bind("change", function(){
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
                    '<label class="checkbox-inline"><input name="tag" type="checkbox" value="{0}"> {1}</label>', 
                    type_tags[i][0], 
                    type_tags[i][1]
                )
            );
        };
    });


    // 按钮点击事件 IE直接点还不行,非要js
    $('.not-login .btn-login').bind('click', function(){
        window.location.href = '/login';
    });
    $('.not-login .btn-regist').bind('click', function(){
        window.location.href = '/regist';
    });

    // 回答工具条显示隐藏事件
    $('#ul_replies .list-group-item')
    .bind('mouseenter', function(){
        $(this).find('.reply-tools .auto-hide').show();
    })
    .bind('mouseleave', function(){
        $(this).find('.reply-tools .auto-hide').hide();
    });
    // 评论工具条显示隐藏事件
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

        if(target.css('display') === 'block'){
            target.hide('fast');
        } else {
            target.show('fast');
        }
    });

    // 邀请打开关闭事件
    $('.question-tools .invite').bind('click', function(){
        var target = $(".topic-invite");
      
        if(target.css('display') === 'block'){
            target.hide();
        } else {
            target.show();
        }
    });

    // 回复某人事件
    $('.answer-say-to').bind('click', function(){
        $('.answer-main .zx-textarea').val("@" + $(this).data('user_name') + " ");
        $('.answer-main .zx-textarea').focusEnd();
    });
  
    // 修改问题弹出层自动选中问题类型和标签
    var selectedQuestionType = "{{question.question_type.id}}",
        selectedQuestionTags = "{% for tag in question_tags %}{{tag.id}}-{% endfor %}";
    if (selectedQuestionType){
        // 自动选中问题类型
        $('#sel_question_type').val(selectedQuestionType);
        $('#sel_question_type').change();

        // 自动选中问题标签
        if(selectedQuestionTags){
            var tempTags = selectedQuestionTags.split('-'), 
                tags = {};

            for(var i=0; i<tempTags.length; i++){
                if(tempTags[i]){
                    tags[tempTags[i]] = true;
                }
            }

            $('#div_tags input').filter(function(i){ 
                return tags[$(this).val()]
            }).attr('checked', true);
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
                duration: 500,
                step: function(now, fx) {
                    transformFun(target, now);
                },
                complete: function(){
                    // 旋转到90度后将数字隐藏，将红心显示，
                    isShowHeart ? target.find('.answer-like').show() : target.find('.answer-like').hide();
                    isShowHeart ? target.find('.answer-like-count').hide() : target.find('.answer-like-count').show();
                    // 再旋转到0度
                    jQuery({p: 90}).animate({p: 0}, {
                        duration: 500,
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
                temp.remove();

                parent.find('.answer-like')
                .removeClass('glyphicon-heart-empty')
                .addClass('glyphicon-heart')
                .css({'color': 'red'});

                parent.find('.answer-like-count')
                .text(parseInt(parent.find('.answer-like-count').text()) + 1);
            });
        });
    });

    // 精华盖章动画
    var jinghua = $('.jinghua img');
    jinghua.show()
    .css({'width': '444.5px', 'height': '385px'})
    .animate({'width': '254', 'height': '220px', 'opacity': '0.6'}, 500)
    .animate({'width': '102px', 'height': '88px', 'opacity': '0.99'}, 50);

});