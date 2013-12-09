# -*- coding: utf-8 -*-
import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

from django.test import TestCase
from common import utils
from django.utils.encoding import smart_str


class SimpleTest(TestCase):

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
        self.assertTrue(True)
        self.assertFalse(False)

    def runTest(self):
        pass

    def test_regist(self):
        from www.account import interface
        ub = interface.UserBase()
        # print ub.set_password(raw_password='123')
        # print ub.check_password(raw_password='123')
        flag, result =  ub.regist_user(email='lantian-lz@163.com', nick='simplejoy', password='851129', ip='127.0.0.1')
        if not flag:
            print result.__repr__()
            print result.encode('utf-8')
        else:
            print result
        return 'ok'


if __name__ == '__main__':
    st = SimpleTest()
    # print st.test_basic_addition()
    # print utils.uuid_without_dash()
    print st.test_regist()
