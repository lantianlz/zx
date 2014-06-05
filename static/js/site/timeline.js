$(document).ready(function(){

    var data = [{
        'content': '新增功能：邀请回答功能上线，提问从此不再孤独！',
        'important': false,
        'noticeId': 11
    }];
    data = [];

    // 获取cookie里面的通知状态
    var localStatus = JSON.parse($.cookie('notices') || '{}');
    
    $.map(data, function(d){
        // 如果没有关闭过，则创建提示
        if(!localStatus[d.noticeId]){
            $.ZXNotice.InlineNotice(
                d.noticeId,
                d.content, 
                $('.new-notices'), 
                d.important,
                function(noticeId){
                    // 关闭之后，更新cookie
                    var tempLocalStatus = JSON.parse($.cookie('notices') || '{}');
                    tempLocalStatus[noticeId] = true;

                    $.cookie('notices', JSON.stringify(tempLocalStatus), {expires: 30});
                }
            );
        }
    });


    var Feed = Backbone.Model.extend({
        defaults: {
            'feedId': '',           // 动态id 
            'feedDate': '',         // 动态时间
            'feedType': 0,          // 动态类型 (1提问 2赞回答 3回答)
            'userId': '',           // 用户id
            'userAvatar': '',       // 用户头像
            'userName': '',         // 用户名
            'questionId': 0,        // 提问id
            'questionTitle': '',    // 提问标题
            'questionDesc': '',     // 提问描述
            'questionViewCount': 0, // 提问浏览次数
            'questionAnswerCount':0,// 提问回答个数
            'answerId': 0,          // 回答id
            'answerContent': '',    // 回答内容
            'answerUserId': '',     // 回答者id
            'answerUserName': '',   // 回答者名字
            'answerUserAvatar': '', // 回答者头像
            'answerUserDesc': '',   // 回答者个人简介
            'answerLikeCount': 0    // 回答获赞个数
        }
    });
    var User = Backbone.Model.extend({
        defaults: {
            'userId': '',           // 用户id
            'userName': '',         // 用户名称
            'userAvatar': '',       // 用户头像
            'userGender': '',       // 用户性别
            'userDesc': '暂无简介',  // 用户简介
            'likeCount': 0,         // 获赞个数
            'answerCount': 0,       // 回答个数
            'questionCount': 0      // 提问个数
        }


    });


    var Feeds = Backbone.Collection.extend({
        model: Feed,

        _modelMaps: {
            'feedId': 'feed_id',           
            'feedDate': 'create_time',         
            'feedType': 'feed_type',         
            'userId': 'user_id',           
            'userAvatar': 'user_avatar',       
            'userName': 'user_nick',         
            'questionId': 'question_id',       
            'questionTitle': 'question_title',   
            'questionDesc': 'question_summary',     
            'questionViewCount': 0, 
            'questionAnswerCount': 'question_answer_count',
            'answerId': 'answer_id',          
            'answerContent': 'answer_summary',    
            'answerUserId': 'answer_user_id',     
            'answerUserName': 'answer_user_nick',   
            'answerUserAvatar': 'answer_user_avatar', 
            'answerUserDesc': 'answer_user_des',   
            'answerLikeCount': 'answer_like_count'    
        },

        // 获得最后一个feedId
        getLastFeedId: function(){
            if(this.length > 0){
                return this.models[this.length - 1].get('feedId');
            }

            return null;
        },

        // 查询
        search: function(feedId){

            var me = this;

            g_ajax_processing_obj_id = 'loadingMoreFeed';
            ajaxSend("/timeline/get_user_timeline", {'last_feed_id': feedId}, function(data){
                if(data.feeds){
                    me.reset($.ZXUtils.dictMapParse(data.feeds, me._modelMaps));
                }

                // 需要推荐用户
                if(data.need_get_recommended_user){
                    recommendUsersView.collection.search(false);
                }
            });

            return this;
        }
    });
    var Users = Backbone.Collection.extend({
        model: User,

        _modelMaps: {
            'userId': 'user_id',           
            'userName': 'nick',         
            'userAvatar': 'avatar',       
            'userGender': 'gender',       
            'userDesc': 'des',
            'likeCount': 'user_liked_count',
            'answerCount': 'user_answer_count',
            'questionCount': 'user_question_count'
        },

        // 加载推荐用户
        search: function(random){
            var me = this;

            g_ajax_processing_obj_id = $('.recommend-users .refresh').setUUID().attr('id');
            ajaxSend("/account/get_recommend_users", {'random': random?'1':'0'}, function(data){
                if(data){
                    me.reset($.ZXUtils.dictMapParse(data, me._modelMaps));
                }
            });

            return this;
        }
    });

    var FeedView = Backbone.View.extend({
        el: '.feed-list',

        template: _.template($('#feed-template').html()),

        // 查看更多模板
        getMoreTemplate: _.template($('#getMore-template').html()),

        events: {
            'click .get-more': 'getMore'
        },

        initialize: function(){
            // 监听集合的reset事件
            this.listenTo(this.collection, 'reset', this.getFeed);

            // 首次查询
            this.collection.search();

        },

        render: function(data){
            this.$el.append(this.template({'feeds': data}));

            // 初始化名片
            $.ZXTooltipster.PersonCard();
        },

        renderGetMore: function(feedId){
            this.$el.append(this.getMoreTemplate({'feedId': feedId}));
        },

        // 根据最后一个feedId 获取之后的feed
        getFeed: function(){
            var data = this.collection.toJSON(),
                lastFeedId = this.collection.getLastFeedId();
            
            this.render(data);

            // 去掉上次的 查看更多 按钮
            this.$('.get-more').parents('li').remove();
            // 是否显示更多
            if(lastFeedId){
                this.renderGetMore(lastFeedId);
            }
        },

        // 查看更多
        getMore: function(){
            var feedId = this.$('.get-more').data('feed_id');
            
            // 隐藏原先的 查看更多 按钮
            this.$('.get-more').hide();

            this.collection.search(feedId);
        }

    });
    var RecommendUsersView = Backbone.View.extend({
        el: '.recommend-users',

        template: _.template($('#recommendUsers-template').html()),

        events: {
            'click .refresh': 'refreshUser',
            'click .follow': 'followUser',
            'click .unfollow': 'unfollowUser'
        },

        initialize: function(){
            // 监听集合的reset事件
            this.listenTo(this.collection, 'reset', this.getRecommendUsers);

            // 首次查询
            //this.collection.search(false)
        },

        render: function(data){
            this.$el.show();
            this.$('.list-inline').html(this.template({'users': data}));
        },

        // 获取推荐用户
        getRecommendUsers: function(){
            var data = this.collection.toJSON();

            this.render(data);
        },

        // 换一换
        refreshUser: function(){
            this.$('ul').fadeOut(300);
            this.collection.search(true)
            this.$('ul').fadeIn(300);
        },

        // 关注用户
        followUser: function(sender){
            var target = $(sender.currentTarget),
                userId = target.data('user_id');

            $.ZXOperation.followPeople(userId, function(){
                target.hide();
                target.next().show();
            });
        },

        // 取消关注
        unfollowUser: function(sender){
            var target = $(sender.currentTarget),
                userId = target.data('user_id');

            $.ZXOperation.unfollowPeople(userId, function(){
                target.hide();
                target.prev().show();
            });
        }
    });


    var feeds = new Feeds(),
        users = new Users(),
        feedView = new FeedView({'collection': feeds}),
        recommendUsersView = new RecommendUsersView({'collection': users});
});