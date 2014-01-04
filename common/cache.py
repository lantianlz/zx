# -*- coding: utf-8 -*-

import redis
from cPickle import dumps, loads


CACHE_TMP = ('127.0.0.1', 6379, 5, 'tmp')
CACHE_STATIC = ('127.0.0.1', 6379, 6, 'static')
CACHE_SESSION = ('127.0.0.1', 6379, 7, 'session')

CONNECTIONS = {}


class Cache(object):

    def __init__(self, config=CACHE_TMP):
        '''
        @note: 采用长连接的方式
        '''
        global CONNECTIONS
        if config[3] not in CONNECTIONS:
            pool = redis.ConnectionPool(host=config[0], port=config[1], db=config[2])
            CONNECTIONS[config[3]] = pool
        else:
            pool = CONNECTIONS[config[3]]

        self.conn = redis.Redis(connection_pool=pool)

    def get(self, key, original=False):
        '''
        @note: original表示是否是保存原始值，用于incr这样的情况
        '''
        obj = self.conn.get(key)
        if obj:
            return loads(obj) if not original else obj
        return None

    def set(self, key, value, time_out=0, original=False):
        s_value = dumps(value) if not original else value
        if time_out:
            if self.conn.exists(key):
                self.conn.setex(key, s_value, time_out)
            else:
                self.conn.setnx(key, s_value)
                self.conn.expire(key, time_out)
        else:
            self.conn.set(key, s_value)

    def delete(self, key):
        return self.conn.delete(key)

    def incr(self, key, delta=1):
        return self.conn.incrby(key, delta)

    def decr(self, key, delta=1):
        return self.conn.decr(key, delta)

    def exists(self, key):
        return self.conn.exists(key)

    def get_time_is_locked(self, key, time_out):
        '''
        @note: 设置锁定时间
        '''
        key = "tlock:%s" % key
        if self.conn.exists(key):
            return True
        self.conn.set(key, 0, time_out)
        return False

    def flush(self):
        self.conn.flushdb()


if __name__ == '__main__':
    import sys
    import os
    sys.path.extend(['../../', ])
    sys.path.extend(['../../../', ])
    os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

    cache_obj = Cache()
    print cache_obj.get_time_is_locked(u'key', time_out=10)
