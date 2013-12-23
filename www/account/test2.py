# -*- coding: utf-8 -*-
from django.conf import settings
from django.test import TestCase

class AccountTestCase(TestCase):
    '''
    调用方法：
    python manage.py test account.test2
    python manage.py test account.test2.AccountTestCase
    python manage.py test account.test2.AccountTestCase.test_hello
    '''
    def setUp(self):
        '''
        测试初始化
        '''
        self.name = 'lei'
    
    def tearDown(self):
        '''
        测试结束操作
        '''
        pass
    
    def test_hello(self):
        self.assertEqual(1+1, 2)
        print settings.DEBUG
