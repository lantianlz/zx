$(document).ready(function(){
    // 鼠标移动到图片淡入淡出效果
    $('.img-fade-hover').imgFadeHover();
    

    // 登记按钮页面跳转
    $('.regist').bind('click', function(){
        //window.location.href = '/regist';
        $.ZXMsg.alert('提示', '网站内测中，只能通过邀请注册，邀请码获取可以联系QQ: 2659790310', 0);
    });


    // 表单验证
    $('.login-form form').validate();
});