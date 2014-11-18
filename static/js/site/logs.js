$(document).ready(function(){
    var Log = Backbone.Model.extend({
        defaults: {
            'year': '2014年',
            'date': '05月05日',
            'contents': []
        }
    });

    var Logs = Backbone.Collection.extend({
        model: Log,

        setData: function(){
            this.reset([
                {'count': 7, 'year': '2014年', 'date': '11月12日', 'contents': _.map([
                    '智选出品的第一款手机app上线，ios和Android齐发，各大应用商店搜索「股票开户宝」即可下载，欢迎踊跃评论'
                ], function(content){return String.format('<li><p>{0}</p></li>', content)}).join('')},

                {'count': 6, 'year': '2014年', 'date': '09月12日', 'contents': _.map([
                    '新增股票模块，数千支个股的最新动态一目了然',
                    '微头条栏目上线，为你精选最好的金融资讯和独到观点'
                ], function(content){return String.format('<li><p>{0}</p></li>', content)}).join('')},

                {'count': 5, 'year': '2014年', 'date': '07月12日', 'contents': _.map([
                    '新增邮件提醒功能，相关个人动态，第一时间发送邮件通知',
                    '新增智选每周精选，每周一自动发出，欢迎查收',
                    '智选微信公众号支持菜单，互动更简单，欢迎订阅，二维码在网站右侧下方',
                    '专题频道正式上线，精彩专题不容错过',
                    '新增搜索功能'
                ], function(content){return String.format('<li><p>{0}</p></li>', content)}).join('')},

                {'count': 4, 'year': '2014年', 'date': '06月12日', 'contents': _.map([
                    '邀请回答功能上线，提问从此不再孤单',
                    '回答处增加点赞人员展示，谁赞了回答一目了然',
                    '提问详情页图片增加图片放大功能，大图小图尽在掌握',
                    '增加全站通告，智选最新功能变化第一时间广而告之'
                ], function(content){return String.format('<li><p>{0}</p></li>', content)}).join('')},

                {'count': 3, 'year': '2014年', 'date': '05月12日', 'contents': _.map([
                    '新增关注用户功能',
                    '新增话题广场',
                    '新增用户名片、话题名片功能',
                    '新增时间线功能，显示关注用户动态信息',
                    '优化手机、平板访问体验'
                ], function(content){return String.format('<li><p>{0}</p></li>', content)}).join('')},

                {'count': 2, 'year': '2014年', 'date': '04月06日', 'contents': _.map([
                    '新增提问回答分享到微博、腾讯QQ',
                    '新增分享赞到微博、腾讯QQ',
                    '新增上传头像裁剪功能',
                    '文本编辑器优化',
                    '开放智选日报公众号，扫描二维码关注',
                    '开放智选交流群: 375931749',
                    '开放<a class="co3 pl-5" target="_blank" href="http://weibo.com/zhixuancom">智选官方微博</a>'
                ], function(content){return String.format('<li><p>{0}</p></li>', content)}).join('')},

                {'count': 1, 'year': '2014年', 'date': '03月12日', 'contents': _.map([
                    '智选横空出世，正式开放内测'
                ], function(content){return String.format('<li><p>{0}</p></li>', content)}).join('')}
            ]);

        }
    });

    var LogView = Backbone.View.extend({
        el: '.logs',

        template: _.template($('#log-template').html()),

        initialize: function(){
            this.listenTo(this.collection, 'reset', this.render);

            this.collection.setData();
        },

        render: function(){
            this.$el.html(
                this.template(
                    {'logs': this.collection.toJSON()}
                )
            );

            // 设置波纹
            this.$('.hidden-xs').eq(0).append('<span class="wave"></span>');
        }
    });

    var logs = new Logs(),
        logView = new LogView({collection: logs});
});
