$(document).ready(function(){
    var isInit = false;

    // 搜索框的动画效果
    $('.navbar .search-input')
    .bind('focus', function(){
        var me = $(this);

        me.attr('placeholder', '搜索提问、回答或者人...');

        $('.navbar .search-container').stop(1,1).animate({'width': 500}, 450, 'easeOutQuart', function(){
            me.select();

            if(isInit){
                return;
            }

            $('.navbar .search-input').autocomplete({
                serviceUrl: '/search_auto_complete',
                paramName: 'key',
                width: 500,
                deferRequestBy: 300,
                showDelay: 500,
                isLocal: false,
                maxHeight: 600,
                autoSelectFirst: false,
                triggerSelectOnValidInput: false,
                transformResult: function(response) {
                    
                    var data = JSON.parse(response),
                        result = [],
                        modelMaps = {
                            "type": "type", 
                            "value": "value", 
                            "data": "data", 
                            "des": "des",
                            "avatar": "avatar", 
                            "answerCount": "answer_count", 
                            "url": "url"
                        };

                    if(data){
                        result = $.ZXUtils.dictMapParse(data, modelMaps);
                        result.push({
                            'type': 'link',
                            'value': "0",
                            'data': '点击查看所有搜索结果',
                            'url': '/search?key_words='+me.val()+'&type=question'
                        })
                    }
                    return {"suggestions": result};
                },
                onSelect: function(suggestion){
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
                                suggestion.des
                            );
                            break;

                        case 'question':
                            html = String.format([
                                '<div class="pointer pt-10 pb-10 pr-20 pl-5 bdc-eee bottom-border pr">',
                                    '<div class="f12">',
                                        '{0}<span class="co8 f12 pl-5">{1} 个回答</span>',
                                        '<span class="pa fa fa-question f18 co17" style="right: 10px; top: 10px;"></span>',
                                    '</div>',
                                '</div>'
                                ].join(''),
                                suggestion.data,
                                suggestion.answerCount
                            );
                            break;
                        default: 
                            html = String.format([
                                '<div class="pointer bgc-e9e9e9 text-center pt-10 pb-10">{0}</div>'
                                ].join(''),
                                suggestion.data
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