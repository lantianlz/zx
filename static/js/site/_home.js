$(document).ready(function(){
    var isInit = false;

    // 搜索框的动画效果
    $('.navbar .search-input')
    .bind('focus', function(){
        $(this).attr('placeholder', '搜索提问、话题或者人...');
        // $('.navbar .search-container').css({'width': 500});

        // if(isInit){
        //  return;
        // }

        // $('.navbar .search-input').autocomplete({
        //     serviceUrl: '/account/get_user_info_by_nick',
        //     paramName: 'user_nick',
        //     // appendTo: '#search_suggestions',
        //     width: 500,
        //     isLocal: false,
        //     autoSelectFirst: true,
        //     triggerSelectOnValidInput: false,
        //     transformResult: function(response) {
                
        //         var data = JSON.parse(response),
        //             result = [];

        //         if(data){
        //             result = [{
        //                 value: data.nick,
        //                 data: data.user_id,
        //                 desc: data.des,
        //                 avatar: data.avatar
        //             }];
        //         }
        //         return {
        //             suggestions: result
        //         };
        //     },
        //     onSelect: function(suggestion){
        //         console.log(suggestion)
                
        //      window.location.href = "/p/" + suggestion.data;

        //     },
        //     formatResult: function(suggestion, value){
        //         return String.format(
        //             '<div class="pointer"><img class="avatar-35 avatar-circle" src="{0}"><span class="pl-5">{1}</span></div>', 
        //             suggestion.avatar, 
        //             suggestion.value
        //         );
        //     }
        // });

        // isInit = true;


        $('.navbar .search-container').stop(1,1).animate({'width': 500}, 450, 'easeOutQuart', function(){
            if(isInit){
                return;
            }

            $('.navbar .search-input').autocomplete({
                serviceUrl: '/account/get_user_info_by_nick',
                paramName: 'user_nick',
                // appendTo: '#search_suggestions',
                width: $.ZXUtils.isPhone() ? 'auto' : 500,
                deferRequestBy: 300,
                showDelay: 500,
                isLocal: false,
                autoSelectFirst: true,
                triggerSelectOnValidInput: false,
                transformResult: function(response) {
                    
                    var data = JSON.parse(response),
                        result = [];

                    if(data){
                        result = [{
                            value: data.nick,
                            data: data.user_id,
                            desc: data.des,
                            avatar: data.avatar
                        }];
                    }
                    return {
                        suggestions: result
                    };
                },
                onSelect: function(suggestion){
                    console.log(suggestion)
                    
                    window.location.href = "/p/" + suggestion.data;

                },
                formatResult: function(suggestion, value){
                    return String.format(
                        '<div class="pointer"><img class="avatar-35 avatar-circle" src="{0}"><span class="pl-5">{1}</span></div>', 
                        suggestion.avatar, 
                        suggestion.value
                    );
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