$(document).ready(function(){
    var isInit = false;

    // 搜索框的动画效果
    $('.navbar .search-input')
    .bind('focus', function(){
        var me = $(this);

        me.attr('placeholder', '搜索提问、话题或者人...');

        $('.navbar .search-container').stop(1,1).animate({'width': 500}, 450, 'easeOutQuart', function(){
            me.select();

            if(isInit){
                return;
            }

            $('.navbar .search-input').autocomplete({
                serviceUrl: '/account/get_user_info_by_nick',
                paramName: 'user_nick',
                width: 500,
                deferRequestBy: 300,
                showDelay: 500,
                isLocal: false,
                autoSelectFirst: true,
                triggerSelectOnValidInput: false,
                transformResult: function(response) {
                    
                    var data = JSON.parse(response),
                        result = [];

                    // if(data){
                    //     result = [{
                    //         value: data.nick,
                    //         data: data.user_id,
                    //         desc: data.des,
                    //         avatar: data.avatar
                    //     }];
                    // }
                    return {
                        suggestions: [{
                                type: 'user',
                                value: '1', 
                                data: '智选创始人', 
                                desc: '暂无简介', 
                                avatar: 'http://img0.zhixuan.com/avatar_17ee2dd6ae3f11e3867d00163e003240',
                                url: 'http://www.a.com:8000/p/2299e654aa6011e3ac1c00163e003240'
                            }, {
                                type: 'user',
                                value: '2', 
                                data: '智选五毛', 
                                desc: '善吐槽，爱折腾，爱户外，爱你妹 力争每日三吐槽，每日放三炮...', 
                                avatar: 'http://img0.zhixuan.com/avatar_d97317d6ae4011e3867d00163e003240',
                                url: 'http://www.a.com:8000/p/cf6e8770aa7b11e3ac1c00163e003240'
                            }, {
                                type: 'question',
                                value: '3', 
                                data: '智选（002474）昨日涨停，今日又早盘放量的票...', 
                                answerCount: 12, 
                                url: 'http://www.a.com:8000/question/184'
                            }, {
                                type: 'question',
                                value: '4', 
                                data: 'MSCI：决定不将智选纳入影响？', 
                                answerCount: 5, 
                                url: 'http://www.a.com:8000/question/183'
                            }
                        ]
                    };
                },
                onSelect: function(suggestion){
                    console.log(suggestion)
                    
                    window.location.href = suggestion.url;
                },
                formatResult: function(suggestion, value){
                    var html = '';

                    // 根据类型渲染模板
                    switch(suggestion.type){
                        case 'user':
                            html = String.format([
                                '<div class="pointer pr pt-10 pb-10 pr-20 pl-5 bdc-eee bottom-border">',
                                    '<img class="avatar-35 avatar-circle pa" src="{0}">',
                                    '<div class="pl-45">',
                                        '<div class="f14">{1}</div>',
                                        '<div class="co8 f12">{2}</div>',
                                    '</div>',
                                    '<span class="pa fa fa-user f16 co17" style="right: 10px; top: 16px;"></span>',
                                '</div>'
                                ].join(''),
                                suggestion.avatar, 
                                suggestion.data,
                                suggestion.desc
                            );
                            break;

                        case 'question':
                            html = String.format([
                                '<div class="pointer pt-10 pb-10 pr-20 pl-5 bdc-eee bottom-border pr">',
                                    '<div class="f12">',
                                        '{0}<span class="co8 f12">{1} 个回答</span>',
                                        '<span class="pa fa fa-question f18 co17" style="right: 10px; top: 10px;"></span>',
                                    '</div>',
                                '</div>'
                                ].join(''),
                                suggestion.data,
                                suggestion.answerCount
                            );
                            break;
                    }

                    return html;
                }
            });

            isInit = true;
        });
        

    })
    .bind('blur', function(){
        $(this).attr('placeholder', '搜索...');
        $('.navbar .search-container').stop(1,1).animate({'width': 130}, 500, 'easeOutQuart');
    });

    // 手机端搜索框大小控制
    $('.navbar .xs-search-container')
    .css({
        'width': $('.zx-header').width() - 100 - 55
    });


    

});