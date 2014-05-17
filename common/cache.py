# -*- coding: utf-8 -*-

import redis
from cPickle import dumps, loads


CACHE_TMP = ('127.0.0.1', 6379, 5, 'tmp')
CACHE_STATIC = ('127.0.0.1', 6379, 6, 'static')
CACHE_USER = ('127.0.0.1', 6379, 7, 'user')
CACHE_SESSION = ('127.0.0.1', 6379, 8, 'session')
CACHE_TIMELINE = ('127.0.0.1', 6379, 9, 'timeline')

CONNECTIONS = {}


def get_connection(config):
    global CONNECTIONS
    if config[3] not in CONNECTIONS:
        pool = redis.ConnectionPool(host=config[0], port=config[1], db=config[2])
        connection = CONNECTIONS[config[3]] = redis.Redis(connection_pool=pool)
    else:
        connection = CONNECTIONS[config[3]]
    return connection


class Cache(object):

    def __init__(self, config=CACHE_TMP):
        '''
        @note: 采用长连接的方式
        '''
        self.conn = get_connection(config)

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

        #self.conn.setex(key, '0', time_out)
        self.set(key, 0, time_out)
        return False

    def flush(self):
        self.conn.flushdb()


class CacheQueue(Cache):

    '''
    @note: 基于redis的list结构设计一个固定长度的队列
    '''

    def __init__(self, key, max_len, time_out=0, config=CACHE_TIMELINE):
        self.key = "queue_%s" % key
        self.max_len = max_len
        self.time_out = time_out
        self.conn = get_connection(config)

    def push(self, item):
        if self.conn.llen(self.key) < self.max_len:
            self.conn.lpush(self.key, item)
        else:
            def _push(pipe):
                pipe.multi()
                pipe.rpop(self.key)
                pipe.lpush(self.key, item)

            self.conn.transaction(_push, self.key)
        if self.time_out:
            self.conn.expire(self.key, self.time_out)
        # print self.conn.lrange(self.key, 0, -1)

    def pop(self, value, num=0):
        self.conn.lrem(self.key, value, num)

    def init(self, items):
        '''
        @note: 初始化一个列表
        '''
        self.delete()
        if items:
            self.conn.rpush(self.key, *items)

    def delete(self):
        self.conn.delete(self.key)

    def exists(self):
        return self.conn.exists(self.key)

    def __getslice__(self, start, end):
        if not self.conn.exists(self.key):
            return None
        return self.conn.lrange(self.key, start, end)


def get_or_update_data_from_cache(_key, _expire, _cache_config, _must_update_cache, _func, *args, **kwargs):
    '''
    @note: 自动缓存方法调用对应的结果，形参名前加下_防止出现重名的和args冲突
    设置data的时候不要设置None值，通过None值来判断是否设置过缓存
    '''
    cache_obj = Cache(config=_cache_config)
    data = cache_obj.get(_key)
    if data is None or _must_update_cache:
        data = _func(*args, **kwargs)
        cache_obj.set(_key, data, time_out=_expire)
    return data


if __name__ == '__main__':
    import sys
    import os
    sys.path.extend(['../../', ])
    sys.path.extend(['../../../', ])
    os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

    cache_obj = Cache()
    # print cache_obj.set(u'keyaaom@a.c!@#$%^&*()om', 'aaa', time_out=1000)

    cache_queue = CacheQueue('test', 5)
    # cache_queue.push('7')
    print cache_queue[0:-1]
    print cache_queue.init(items=[1, 2, 3, 4, 5])
