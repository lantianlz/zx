# -*- coding: utf-8 -*-


class QuestionRouter(object):

    """ 
    @attention: 一个控制 question 应用中模型的 所有数据库操作的路由 
    """
    db_name = 'question'
    app_name = 'question'

    def db_for_read(self, model, **hints):
        """
        @attention: question 应用中模型的操作指向 'questions'
        """
        if model._meta.app_label == self.app_name:
            return self.db_name
        return None

    def db_for_write(self, model, **hints):
        """
        @attention: question 应用中模型的操作指向 'questions'
        """
        if model._meta.app_label == self.app_name:
            return self.db_name
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """ 
        @attention: 如果包含 question 应用中的模型则允许所有关系 
        """
        if obj1._meta.app_label == self.app_name or obj2._meta.app_label == self.app_name:
            return True
        return None

    def allow_syncdb(self, db, model):
        """
        @attention: 确保 question 应用只存在于 'questions' 数据库 
        """
        if db == self.db_name:
            return model._meta.app_label == self.app_name
        elif model._meta.app_label == self.app_name:
            return False
        return None
