$(document).ready(function(){
    $('.topic-item .btn-follow').bind('click', function(){
        var target = $(this).parents('.topic-item').eq(0).find('.zx-topictips');

        $.ZXMsg.alert('关注话题', target.data('topic_id'));
    });
    $('.topic-item .btn-unfollow').bind('click', function(){
        var target = $(this).parents('.topic-item').eq(0).find('.zx-topictips');

        $.ZXMsg.alert('取消关注话题', target.data('topic_id'));
    })
});