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
        字典映射

        用例：
        $.ZXUtils.dictMap({'a': '1', 'b': '2'}, {'a': 'a1', 'b': 'b1'})
        返回 {'a1': '1', 'b1': '2'}
    */
    $.ZXUtils.dictMap = function(originDict, maps){
        var newDict = {};
        
        if(!originDict){
            return null;
        }
        
        for(var m in maps){
            newDict[m] = originDict[maps[m]]
        }

        return newDict;
    };

    /*
        批量字典映射解析

        $.ZXUtils.dictMapParse([{'a': '1', 'b': '2'}], {'a': 'a1', 'b': 'b1'});
    */
    $.ZXUtils.dictMapParse = function(data, maps){
        var temp = [];

            _.each(data, function(d){
                temp.push($.ZXUtils.dictMap(d, maps));
            });

        return temp;
    };


    /*
        自动补零
        始终返回两位字符串，不够自动补零

        用例:
        $.ZXUtils.addZero('0');
    */
    $.ZXUtils.addZero = function(data){
        var temp = data + '';
        if(temp.length === 0){
            return '00'
        } else if(temp.length === 1){
            return  '0' + temp;
        } else{
            return data;
        }
    };


    /*
        格式化日期
        返回字符串  可带格式 y-m-d、h:m:s、y-m-d h:m:s

        用例:
        $.ZXUtils.formatDate(new Date());
        $.ZXUtils.formatDate(new Date(), 'y-m-d');
    */
    $.ZXUtils.formatDate = function(date, format){

        var str = "",
            year = $.ZXUtils.addZero(date.getFullYear()),
            month = $.ZXUtils.addZero(date.getMonth()+1), 
            day = $.ZXUtils.addZero(date.getDate()),
            hours = $.ZXUtils.addZero(date.getHours()),
            minutes = $.ZXUtils.addZero(date.getMinutes()),
            seconds = $.ZXUtils.addZero(date.getSeconds());

        switch(format){
            case 'y-m-d': 
                str = String.format('{0}-{1}-{2}', year, month, day);
                break;
            case 'h:m:s':
                str = String.format('{0}:{1}:{2}', hours. minutes, seconds);
                break;
            default:
                str = String.format('{0}-{1}-{2} {3}:{4}:{5}', year, month, day, hours, minutes, seconds);
                break;
        }
        return str;

    };

    /*
        将表单数据转换成字典，用于ajax

        用例:
        $.ZXUtils.formToDict('myform');
    */
    $.ZXUtils.formToDict = function(selector){
        var postData = {};

        // 转换
        _.map($(selector).serializeArray(), function(i){
            if(i.value){
                postData[i.name] = i.value
            }
        });

        return postData;
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


    // 地图插件
    $.ZXMap = (function(){
        var map = null,
            mapHtml = [
            '<div class="modal fade" id="map_modal" role="dialog">',
                '<div class="modal-dialog map-modal-dialog">',
                    '<div class="modal-content">',
                        '<div class="modal-header">',
                            '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>',
                            '<h4 class="modal-title"></h4>',
                        '</div>',
                        '<div class="modal-body pb-0">',
                            '<div id="zx_map" style="height: 500px;"></div>',
                        '</div>',
                    '</div>',
                '</div>',
            '</div>'
        ].join('');

        return {
            version: '1.0.0',
            author: 'stranger',
            description: '地图插件',
            createMap: function(mapTitle){
                if(!map){
                    // 是否第一次创建地图框
                    if($('#map_modal').length == 0){
                        // 将反馈框添加进body
                        $('body').append(mapHtml);
                    }

                    // 创建百度地图对象
                    map = new BMap.Map("zx_map");
                }

                // 设置地图title
                $('#map_modal .modal-title').html(mapTitle);
                // 显示
                $('#map_modal').modal({'show': true});//, 'backdrop': 'static'});

                return map;
            }
        };
    })();
    
    /*
        根据地址名称定位
        addressName: 地址名称

        用例:
        $.ZXMap.locationByName("理想中心");
    */
    $.ZXMap.locationByName = function(addressName){
        var map = $.ZXMap.createMap(addressName);

        //地址解析器
        var myGeo = new BMap.Geocoder();
        
        myGeo.getPoint(addressName, function(point){
            
            if(point){
                //启用滚轮放大缩小
                map.enableScrollWheelZoom();
                //初始化地图,设置中心点坐标和地图级别
                map.centerAndZoom(point, 16);
                //添加平移缩放控件
                map.addControl(new BMap.NavigationControl());
                //添加地图缩略图控件
                map.addControl(new BMap.OverviewMapControl());

                //创建标注（类似定位小红旗）
                var marker = new BMap.Marker(point);
                //标注提示文本
                //var label = new BMap.Label(lableName, {"offset":new BMap.Size(20,-20)});
                //marker.setLabel(label); //添加提示文本

                //创建消息框
                var infoWindow = new BMap.InfoWindow(addressName);
                //绑定标注单击事件，设置显示的消息框
                marker.addEventListener("click", function(){
                    this.openInfoWindow(infoWindow);
                });

                //把标注添加到地图
                map.addOverlay(marker);
            }
        }, "成都");
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
        $.ZXMsg.confirm('提示', '确认要取消关注吗?', function(result){
            if(result){
                ajaxSend("/timeline/unfollow/" + userId, {}, callback, 'GET');
            }
        });
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
                        '<a href="/p/{14}"><img class="avatar avatar-55 avatar-circle ml-10 mt-5" src="{0}" ></a>',
                    '</div>',
                    '<div class="col-md-9">',
                        '<div class="pt-10 pb-5"><a href="/p/{10}">{1}</a>{12}</div>',
                        '<div class="pt-5">',
                            '<span>提问<a href="/p/{15}/questions" class="pl-3 pr-15">{2}</a></span>',
                            '<span>回答<a href="/p/{16}/answers" class="pl-3 pr-15">{3}</a></span>',
                            '<span>赞<a href="javascript: void(0)" class="pl-3 pr-15">{4}</a></span>',
                        '</div>',
                    '</div>',
                '</div>',
                '<div class="desc pl-10 pt-5 w300 co6">{5}</div>',
                '<div class="topics pl-10 pt-10 pb-5 w300 co6 none">擅长话题: {11}</div>',
                '<div class="tools top-border bdc-eee pt-5 mt-5 {13}" data-user_name="{6}" data-user_id="{7}">',
                    '<a class="send-message pr-10 pt-5 pl-5 none" href="javascript: void(0)">',
                        '<span class="glyphicon glyphicon-envelope"></span> 私信ta',
                    '</a>',
                    '<button type="button" class="btn btn-primary btn-xs follow ml-10 mr-5 pull-right {8}">添加关注</button>',
                    '<button type="button" class="btn btn-default btn-xs unfollow mr-5 pull-right {9}">取消关注</button>',
                '</div>',
            '</div>'
        ].join('');

        // 手机访问不要设置弹出名片
        if($.ZXUtils.isPhone()){
            return;
        }

        // 未登录不弹出名片
        if(!CURRENT_USER_ID){
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
                            if(data.user_id){
                                origin.tooltipster('content', String.format(
                                    cardtipsHtml, 
                                    data.avatar,
                                    data.nick, 
                                    data.user_question_count,
                                    data.user_answer_count,
                                    data.user_liked_count,
                                    data.des,
                                    data.nick,
                                    data.user_id,
                                    data.is_follow?'none':'', // 关注按钮
                                    data.is_follow?'':'none', //取消关注按钮
                                    data.user_id,
                                    // 拼装话题
                                    $(data.topics).map(function(){
                                        return  String.format(
                                            '<a class="border-block-blue ml-5 pl-5 pr-5" href="/topic/{0}">{1}</a>', 
                                            this['topic_id'], 
                                            this['topic_name']
                                        )
                                    }).get().join(''),
                                    // 根据性别设置对应的图片
                                    (function(gender){
                                        var genderData = {
                                            '0': '', 
                                            '1': '<img class="w15 mt--2 ml-5" src="'+MEDIA_URL+'img/common/male.png" title="男" />', 
                                            '2': '<img class="w15 mt--2 ml-5" src="'+MEDIA_URL+'img/common/female.png" title="女" />'
                                        }; 
                                        return genderData[gender]
                                    })(data.gender),
                                    CURRENT_USER_ID == data.user_id ? 'none' : '',
                                    data.user_id,
                                    data.user_id,
                                    data.user_id
                                )).data('ajax', 'cached');
                                
                                // 监听清除缓存事件
                                $.ZXEvent.on('removePersonCardCache', function(){
                                    origin.data('ajax', '');
                                });
                            } else {
                                origin.tooltipster('content', '加载名片失败');
                            }
                        }
                    });
                }
            },

            functionReady: function(origin, tooltip){
                
                // 诡异！！
                setTimeout(function(){
                    
                    // 关注事件
                    tooltip.find('.follow').bind('click', function(){
                        var me = $(this), 
                            target = me.parents('.tools').eq(0);
                        
                        //$.ZXMsg.alert('关注人', target.data('user_id') + target.data('user_name'));
                        g_ajax_processing_obj_id = me.setUUID().attr('id');
                        $.ZXOperation.followPeople(target.data('user_id'), function(){
                            target.children('.unfollow').show(1, function(){
                                me.hide(1);
                                
                                // 关注之后需要清除名片的缓存
                                $.ZXEvent.trigger("removePersonCardCache");
                            });
                        });
                        
                    });

                    // 取消关注事件
                    tooltip.find('.unfollow').bind('click', function(){
                        var me = $(this), 
                            target = me.parents('.tools').eq(0);
                        
                        //$.ZXMsg.alert('取消关注', target.data('user_id') + target.data('user_name'));
                        g_ajax_processing_obj_id = me.setUUID().attr('id');
                        $.ZXOperation.unfollowPeople(target.data('user_id'), function(){
                            target.children('.follow').show(1, function(){
                                me.hide(1);
                                
                                // 取消关注之后需要清除名片的缓存
                                $.ZXEvent.trigger("removePersonCardCache");
                            });
                        });

                    });

                    // 从名片上点击发私信事件 
                    tooltip.find('.send-message').bind('click', function(){
                        var target = $(this).parents('.tools').eq(0);
                        $.ZXMsg.sendPrivateMsg(target.data('user_id'), target.data('user_name'));
                    });

                }, 500);
                
            }
        });
        
        
        
    };

    /*
        话题名片
        自动将class为 zx-topictips 的元素注册弹出名片
        需要设置 data-topic_id 属性为话题id

        用例:
        $.ZXTooltipster.TopicCard();
    */
    $.ZXTooltipster.TopicCard = function(){
        // 弹出话题名片设置
        var topictipsHtml = [
            '<div class="topictips f12">',
                '<div class="profile row f14">',
                    '<div class="col-md-3">',
                        '<a href="/topic/{7}"><img class="avatar avatar-55 avatar-circle ml-10 mt-5" src="{0}"></a>',
                    '</div>',
                    '<div class="col-md-9">',
                        '<div class="pt-10 pb-5"><a href="/topic/{7}">{1}</a></div>',
                        '<div class="question-info pt-5">',
                            '<span class="none">关注者<span class="pl-3 pr-15 fb">{2}</span></span>',
                            '<span>提问<span class="pl-3 pr-15 fb">{3}</span></span>',
                        '</div>',
                    '</div>',
                '</div>',
                '<div class="desc pl-10 pt-5 w300 co6">{4}</div>',
                '<div class="none tools top-border bdc-eee pt-5 mt-5 text-right" data-topic_id="{7}">',
                    '<button type="button" class="btn btn-primary btn-xs follow mr-5 ml-10 {5}">添加关注</button>',
                    '<button type="button" class="btn btn-default btn-xs unfollow mr-5 {6}">取消关注</button>',
                '</div>',
            '</div>'
        ].join('');

        // 手机访问不要设置弹出名片
        if($.ZXUtils.isPhone()){
            return;
        }

        // 未登录不弹出名片
        if(!CURRENT_USER_ID){
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
                            if(data.domain){
                                origin.tooltipster('content', String.format(
                                    topictipsHtml, 
                                    data.img,
                                    data.name, 
                                    data.follow_count,
                                    data.question_count,
                                    data.des || '暂无话题介绍',
                                    data.is_follow?'none':'', // 关注按钮
                                    data.is_follow?'':'none', //取消关注按钮
                                    data.domain
                                )).data('ajax', 'cached');

                                // 监听清除缓存事件
                                $.ZXEvent.on('removeTopicCardCache', function(){
                                    origin.data('ajax', '');
                                });
                            } else {
                                origin.tooltipster('content', '加载名片失败');
                            }
                        }
                    });
                }
            },

            functionReady: function(origin, tooltip){
                // 诡异！！
                setTimeout(function(){
                    
                    // 关注事件
                    tooltip.find('.follow').bind('click', function(){
                        var me = $(this),
                            target = $(this).parents('.tools').eq(0);

                        target.children('.unfollow').show(1, function(){
                            me.hide(1);

                            // 关注之后需要清除名片的缓存
                            $.ZXEvent.trigger("removeTopicCardCache");
                        });
                    });

                    // 取消关注事件
                    tooltip.find('.unfollow').bind('click', function(){
                        var me = $(this),
                            target = $(this).parents('.tools').eq(0);

                        target.children('.follow').show(1, function(){
                            me.hide(1);

                            // 取消关注之后需要清除名片的缓存
                            $.ZXEvent.trigger("removeTopicCardCache");
                        });
                    });
                }, 500);
            }
        });
        
        
    };

    /*
        事件对象
    */
    $.ZXEvent = {};
    _.extend($.ZXEvent, Backbone.Events);


    /*
        分页组件
    */
    $.ZXPagination = {
        version: '1.0.0',
        author: 'stranger',
        description: '分页组件'
    }
    /*
        分页组件
    */
    $.ZXPagination.PaginationView = Backbone.View.extend({
        el: '.zx-pagination',

        step: 4,

        totalStep: 10,

        searchUrl: 'search',

        // 防止超出范围
        _protectRange: function(tempMin, tempMax, min, max){
            if(tempMin < min){
                tempMin = min;
            }

            if(tempMax > max){
                tempMax = max
            }

            return [tempMin, tempMax]
        },

        // 生成分页区间
        _generateRange: function(current, total){
            var pages = [], 
                current = parseInt(current),
                total = parseInt(total),
                min = current - this.step,
                max = current + this.step,
                temp = [];

            // 防止超出范围
            temp = this._protectRange(min, max, 1, total);
            min = temp[0];
            max = temp[1];

            // 维持列表在 totalStep-1 这个长度
            var tempCount = max - min + 2;
            if(tempCount < this.totalStep){
                if(max >= total){
                    max = total;
                    min = max - this.totalStep + 2;
                } else {
                    max = this.totalStep - 1;
                }
            }

            // 防止超出范围
            temp = this._protectRange(min, max, 1, total);

            // 生成列表
            pages = _.range(temp[0], temp[1]+1);

            return pages;
        },

        render: function(pageIndex, pageCount, searchUrl){
            var url = searchUrl || this.searchUrl,
                pageHtml = '',
                pages = this._generateRange(pageIndex, pageCount);
            
            for (var i = 0; i < pages.length; i++) {

                pageHtml += String.format(
                    '<li {0}><a href="#{1}/{2}">{3}</a></li>', 
                    pages[i] == pageIndex ? 'class="active"' : '', // 为当前页添加active类
                    url, 
                    pages[i], 
                    pages[i]
                );
            };

            // 首页
            pageHtml = String.format(
                '<li {0}><a href="{1}">&laquo;</a>', 
                pageIndex == 1 ? 'class="disabled"' : '',
                pageIndex == 1 ? 'javascript: void(0);' : ('#' + url + '/' + 1)
            ) + pageHtml;
            
            // 末页
            pageHtml += String.format(
                '<li {0}><a href="{1}">&raquo;</a>', 
                pageIndex == pageCount ? 'class="disabled"' : '',
                pageIndex == pageCount ? 'javascript: void(0);' : ('#' + url + '/' + pageCount)
            );

            this.$el.html(pageHtml);
        }
    });


    /*
        文本框组件
    */
    $.ZXTextboxList = {
        version: '1.0.0',
        author: 'stranger',
        description: '文本框组件'
    };
    /**/
    $.ZXTextboxList.create = function(selector, options){
        var temp = new $.TextboxList(selector, {
            bitsOptions: {
                box: {deleteButton: true}
            },
            unique: true, 
            max: options.max,
            plugins: {
                autocomplete: {
                    minLength: 2, // 最小字符
                    queryRemote: true, // 远程查询
                    placeholder: options.placeholder,
                    highlight: false,
                    onlyFromValues: true, // 是否默认选中第一个结果
                    remote: {
                        url: options.url, 
                        param: options.param,
                        loadPlaceholder: options.loadPlaceholder,
                    }
                }
            }

        });

        return {
            target: temp,
            add: function(name, value){
                temp.add(name, value)
            },
            getValues: function(){
                return _.map(temp.getValues(), function(v){return v[0]});
            }
        };
    };


    /* 
        图表插件
    */
    $.ZXChart = {
        version: '1.0.0',
        author: 'stranger',
        description: '图表插件'
    };
    /*
        通用图表插件

        用例:
        
    */
    $.ZXChart.lineChart = function(_options){
        var options = $.extend(true, {
                title: '',
                subtitle: '',
                categories: [],
                xAxis: '',
                yAxis: '',
                series: []
            }, _options),

            chartHtml = [
                '<div class="modal fade" id="chart_modal" tabindex="-1" role="dialog">',
                    '<div class="modal-dialog" style="width: 1200px;">',
                        '<div class="modal-content">',
                            '<div class="modal-header pb-5">',
                                '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>',
                                '<h4 class="modal-title">'+options.title+'</h4>',
                            '</div>',
                            '<div class="modal-body container" id="chart_body" >',
                                
                            '</div>',
                        '</div>',
                    '</div>',
                '</div>'
            ].join('');

        // 将chart框添加进body
        $('body').append(chartHtml);
        
        // 关闭之后清除掉自己
        $('#chart_modal').on('hidden.bs.modal', function(e){
            $(this).remove();
        });

        var _chart = $('#chart_body').highcharts({
            chart: {
                type: 'line'
            },
            title: {
                text: options.title,
                x: -20 //center
            },
            subtitle: {
                text: options.subtitle,
                x: -20
            },
            xAxis: {
                title: {
                    text: options.xAxis
                },
                categories: options.categories
            },
            yAxis: {
                title: {
                    text: options.yAxis
                }
            },
            // legend: {
            //     layout: 'vertical',
            //     align: 'right',
            //     verticalAlign: 'middle',
            //     borderWidth: 0
            // },
            series: options.series
        });

        // 显示chart框
        $('#chart_modal').modal({'show': true, 'backdrop': 'static'});
        
    };


    /* 
        网站提示插件
    */
    $.ZXNotice = {
        version: '1.0.0',
        author: 'stranger',
        description: '网站提示插件'
    };
    $.ZXNotice.FixNotice = function(){
        var noticeHtml = [
            '<div id="zx_fix_notice" class="none pf co8 box-shadow-224 bgc-000 border-radius-2 pr-15 pb-15 pt-15" style="bottom:3px;right:5px;opacity:1;">',
                '<ul>',
                    '<li>',
                        '上线功能点：',
                    '</li>',
                    '<li>',
                        '1.邀请回答功能上线，提问从此不再孤独',
                    '</li>',
                    '<li>',
                        '2.一句话简介等信息拒绝用户输入纯空格这样的不可见字符',
                    '</li>',
                    '<li>',
                        '3.回答中自己@自己的回答，在@提到我的回答中不进行展示',
                    '</li>',
                    '<li>',
                        '4.本地开发环境中的请求不再往百度统计发送信息，避免干扰统计数据',
                    '</li>',
                '</ul>',
                '<span class="pa glyphicon glyphicon-remove-circle f18 pointer z99" style="top:5px;right:5px;"></span>',
            '</div>'
        ].join('');

        $('body').append(noticeHtml);

        $('#zx_fix_notice').show('fast');

        // 绑定关闭事件
        $('#zx_fix_notice .glyphicon-remove-circle')
        .bind('click', function(){

            // 关闭之后删除整个提醒框
            $('#zx_fix_notice').hide('fast', function(){
                $(this).remove();
            })
        });
    };
    /*
        行内通知
        content: 通知内容
        important: 是否重要通知

        用例:
        $.ZXNotice.InlineNotice(11, '这是通知', '', false, function(){})
    */
    $.ZXNotice.InlineNotice = function(noticeId, content, toElement, important, closeCallback){
        var noticeHtml = [
                '<div class="alert alert-dismissable mb-10 {1} box-shadow-224 border-radius-2 co3 zx-inline-notice none">',
                    '<button type="button" class="close" aria-hidden="true">',
                        '<span class="glyphicon glyphicon-remove-circle co3 f18 pointer remove-inline-notice"></span>',
                    '</button>',
                    '<span class="glyphicon glyphicon-bullhorn pr-10"></span>',
                    '<span class="notice-content">{0}</span>',
                '</div>'
            ].join('');

        var target = $(String.format(noticeHtml, content, important?'bgc-CA7842':'bgc-zx')).appendTo(toElement);

        // 显示
        target.show('fast');
       
        // 绑定回调函数
        target
        .find('.close')
        .bind('click', function(){
            // 关闭之后删除自己
            target.hide('fast', function(){target.remove()});

            if(closeCallback){
                closeCallback(noticeId);
            }
        });
    };

    /*
        顶部通知
        content: 通知内容
        type: 是否重要通知

        用例:
        $.ZXNotice.TopNotice('info', '这是通知', 2000);
    */
    $.ZXNotice.TopNotice = function(type, content, closeSeconds){
        var noticeHtml = [
                '<div class="alert alert-dismissable pf box-shadow-224 border-radius-2 co3 min-w600 zx-top-notice zx-{0}-notice">',
                    '<button type="button" class="close" aria-hidden="true">',
                        '<span class="glyphicon glyphicon-remove-circle co3 f18 pointer"></span>',
                    '</button>',
                    '<span class="glyphicon {1} pa pr-10 f20" style="left: 25px; top: 15px;"></span>',
                    '<span class="notice-content pl-50">{2}</span>',
                '</div>'
            ].join(''),
            // 图标
            signDict = {
                'success': 'glyphicon-ok', 
                'error': 'glyphicon-exclamation-sign',
                'warning': 'glyphicon-warning-sign',
                'info': 'glyphicon-info-sign'
            },
            sign = signDict[type ? type : 'info'];


        var target = $(String.format(noticeHtml, type, sign, content)).appendTo($('body')),
            left = ($(window).width() - target.width()) / 2 - 30;

        target
        .css({'left': left > 0 ? left : 0 , 'top': 0})
        .animate({'top': 55}, 300);

        target
        .find('.close')
        .bind('click', function(){
            // 关闭之后删除自己
            target.animate({'top': 0}, 300, function(){target.remove()});
        });

        // 自动关闭时间
        if(closeSeconds){
            window.setTimeout(function(){
                target.animate({'top': 0}, 300, function(){target.remove()});
            }, closeSeconds);
        }

    };

    // 成功信息
    $.ZXNotice.SuccessTopNotice = function(content){
        $.ZXNotice.TopNotice('success', content, 3000);
    };

    // 错误信息
    $.ZXNotice.ErrorTopNotice = function(content){
        $.ZXNotice.TopNotice('error', content);
    };

    // 普通信息
    $.ZXNotice.InfoTopNotice = function(content){
        $.ZXNotice.TopNotice('info', content, 3000);
    };

    // 警告信息
    $.ZXNotice.WarningTopNotice = function(content){
        $.ZXNotice.TopNotice('warning', content);
    };


    /*
        图片显示插件
    */
    $.ZXImage = {
        version: '1.0.0',
        author: 'stranger',
        description: '图片显示插件'
    };
    /*
        全屏图片显示插件
        originUrl: 原始图片地址
        newUrl：完整图片地址

        用例：
        $.ZXImage.FullImage('XXX.png!600m0', 'XXX.png');
    */
    $.ZXImage.FullImage = function(originUrl, newUrl){
        
        $('#full_image_modal').remove();

        var html = [
                '<div class="modal fade text-center" id="full_image_modal">',
                    '<image src="'+originUrl+'" />',
                    '<div class="loading-img co3">正在加载原始图片...</div>',
                    '<span class="pa glyphicon glyphicon-remove-circle co3 f30 pointer" style="right: 5px; top: 5px;"></span>',
                '</div>'
            ].join('');

        var img = new Image();
        img.style.display = "none";
        img.onload = function(){
            var marginTop = $(window).height() - img.height;
                marginTop = marginTop > 0 ? marginTop / 2 : 0;

            // 隐藏loading
            $('#full_image_modal .loading-img').hide();

            // 动态计算图片位置和大小
            $('#full_image_modal img').animate({
                height: img.height,
                width: img.width,
                marginTop: marginTop
            }, 300, function(){
                $(this).attr('src', newUrl);
                $(img).remove();
            });
        }
        $('body').append(img);
        img.src = newUrl;

        $('body').append(html);

        // 关闭图片事件
        $('#full_image_modal .glyphicon-remove-circle')
        .bind('click', function(){
            $('#full_image_modal').modal('hide');
        })

        $('#full_image_modal').modal('show');
    };

    /*
        进度条插件
    */
    $.ZXProgress = {
        version: '1.0.0',
        author: 'stranger',
        description: '进度条插件'
    };

    /*
        进度条插件

        用例：
        $.ZXImage.ForeverProgress({width: 500, top: 20, left: 30});
    */
    $.ZXProgress.ForeverProgress = function(_options){
        var options = $.extend(true, {
                width: 500,
                top: 0,
                left: 0,
                totalSeconds: 3000,
                per: 300
            }, _options),

            progressHtml = [
                '<div class="progress progress-striped active pa" id="forever_progress" style="top: {0}px; width: {1}px; left: {2}px; z-index: 99999;">',
                    '<div class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%">',
                        '<span class="sr-only">0%</span>',
                    '</div>',
                '</div>'
            ].join(""),
        
            current = 0,
            // 循环添加进度
            progressInterval = window.setInterval(function(){
                
                current += (options.totalSeconds / options.per);
                $('#forever_progress .progress-bar')
                .css({'width': current  + '%'});

                // 如果到100了  重新开始
                if(current >= 100){
                    current = 0;
                }
                
            }, options.per),

            // 删除进度条
            removeProgress = function(){
                window.setTimeout(function(){
                    $('#forever_progress').fadeOut(300, function(){
                        $(this).remove();
                    });
                }, 600);
            };

        // 添加进度条
        $('body').append(String.format(progressHtml, options.top, options.width, options.left));

        return {
            // 完成
            finish: function(){
                window.clearInterval(progressInterval);

                $('#forever_progress .progress-bar').css({'width': '100%'});

                removeProgress();
            },
            // 清除
            remove: function(){
                window.clearInterval(progressInterval);

                removeProgress();
            }
        }
    }

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
            allowPreviewEmoticons : true,
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
                'image', 'link', '|', //'emoticons_zx',
                'fullscreen'
            ],
            afterCreate : function() { 
                //this.loadPlugin('autoheight');
                
                var me = this;

                // 监听 复制事件
                KindEditor(me.edit.doc).bind('paste', function(e){
                    
                    // 添加到事件对象中的访问系统剪贴板的接口
                    var clipboardData = e.event.clipboardData,
                        items,
                        item,
                        // 上传文件方法
                        postImage = function(data){
                            var postData = new FormData(),
                                target = $(selector).prev(),
                                offset = target.offset(),
                                width = target.width();
                                progress = $.ZXProgress.ForeverProgress({
                                    width: width,
                                    top: offset.top + 30,
                                    left: offset.left,
                                    totalSeconds: 5000,
                                    per: 500
                                });

                            // 设置上传数据
                            postData.append("imgFile", data);

                            $.ajax({
                                url: '/save_img',
                                data: postData,
                                dataType: 'json',
                                type: "POST",
                                contentType: false,
                                processData: false,
                                success: function(data){
                                    if(data.error == 0){
                                        // 上传成功插入图片
                                        window.setTimeout(function(){
                                            me.exec('insertimage', data.url);
                                        }, 0);
                                        progress.finish();
                                    } else {
                                        progress.remove();
                                        $.ZXMsg.alert('提示', '图片上传失败');
                                    }
                                },
                                error: function(){
                                    progress.remove();
                                }
                            });
                            
                        };
                        
                    if(clipboardData){
                        items = clipboardData.items;
                        
                        for(var i=0; i<items.length; i++){
                            item = items[i];

                            if(item.kind == 'file' && item.type.indexOf('image/') !== -1){
                                // 上传该图片            
                                postImage(item.getAsFile());
                                break;
                            }
                        }
                    }
                });


                // ctrl + enter 回复
                KindEditor.ctrl(me.edit.doc, 13, function() {
                    $(selector).parents('form').submit();
                });
                me.sync();
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
if(jQuery.validator){
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
}


$(document).ready(function(){
    
    // 回到顶部动画效果
    var userClickTop = false;

    $(window).scroll(
        _.throttle(function(){
            var me = $(this);

            if(!userClickTop){
                if(me.scrollTop() < 400){
                    $('.scroll-top').hide('fast');
                }else{
                    $('.scroll-top').show('fast');
                }
            }
        }, 300)
    );

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
    
    // 电脑访问添加鼠标事件
    if($.ZXUtils.isDesktop()){
        $('.user-menu .dropdown-toggle')
        .bind('mouseenter', function(){showDropdown('.user-menu')})
        .bind('mouseleave', function(){hideDropdown('.user-menu')})
        .bind('click', function(e){
            window.location.href = $(this).attr('href');
        });

        $('.user-menu .dropdown-menu')
        .bind('mouseenter', function(){showDropdown('.user-menu')})
        .bind('mouseleave', function(){hideDropdown('.user-menu')});

        $('.user-notice .dropdown-toggle')
        .bind('mouseenter', function(){showDropdown('.user-notice')})
        .bind('mouseleave', function(){hideDropdown('.user-notice')});

        $('.user-notice .dropdown-menu')
        .bind('mouseenter', function(){showDropdown('.user-notice')})
        .bind('mouseleave', function(){hideDropdown('.user-notice')});
    }


    // 隐藏所有 auto-hide 样式
    $('.auto-hide').hide();

    
    // 用户反馈
    $('.follow-zx .feedback').bind('click', function(){
        $.ZXMsg.feedback();
    });

    // 提示信息框
    try {
        if(ERROR_MSG){
            $.ZXNotice.ErrorTopNotice(ERROR_MSG);
        }
        if(SUCCESS_MSG){
            $.ZXNotice.SuccessTopNotice(SUCCESS_MSG);
        }
        if(INFO_MSG){
            $.ZXNotice.InfoTopNotice(INFO_MSG);
        }
        if(WARNING_MSG){
            $.ZXNotice.WarningTopNotice(WARNING_MSG);
        }
    }
    catch(e) {
        alert(e);
    }

});

