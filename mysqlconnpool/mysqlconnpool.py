#!/usr/bin/env python2
# coding: utf-8

import copy
import logging
import Queue

import MySQLdb

logger = logging.getLogger(__name__)


class MysqlConnectionPool(object):

    def __init__(self, conn_argkw, options=None):

        options = options or {}
        options = copy.deepcopy(options)

        self.options = options
        self.queue = Queue.Queue(32)
        self.conn_argkw = conn_argkw
        if 'host' in conn_argkw:
            self.name = '{host}:{port}'.format(**conn_argkw)
        else:
            self.name = '{unix_socket}'.format(**conn_argkw)

        self.stat = {'name': self.name,
                     'create': 0,
                     'pool_get': 0,
                     'pool_put': 0,
                     }

    def get_conn(self):

        try:
            conn = self.queue.get(block=False)
            self.stat['pool_get'] += 1
            logger.debug('reuse connection:' + repr(self.stat))
            return conn

        except Queue.Empty:

            conn = new_connection(self.conn_argkw, options=self.options)

            self.stat['create'] += 1
            logger.info('create new connection: ' + repr(self.stat))

            return conn

    def put_conn(self, conn):

        try:
            self.queue.put(conn, block=False)
            self.stat['pool_put'] += 1
            logger.debug('put connection:' + repr(self.stat))

        except Queue.Full:
            conn.close()


class ConnectionWrapper(object):

    def __init__(self, pool):
        self.pool = pool
        self.conn = None

    def __enter__(self):
        self.conn = self.pool.get_conn()
        return self.conn

    def __exit__(self, errtype, errval, _traceback):

        if errtype is None:
            self.pool.put_conn(self.conn)
            self.conn = None
        else:
            self.conn.close()


def make(conn_argkw, options=None):

    pool = MysqlConnectionPool(conn_argkw, options=options)

    def pool_api(action=None):

        if action is None or action == 'get_conn':
            return ConnectionWrapper(pool)
        elif action == 'stat':
            return pool.stat
        else:
            raise ValueError(action, 'invalid action: ' + repr(action))

    pool_api.query = lambda *args, **kwargs: query(pool_api, *args, **kwargs)

    return pool_api


def conn_query(conn, sql, use_dict=True):

    if use_dict:
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
    else:
        cur = conn.cursor()

    cur.execute(sql)
    rst = cur.fetchall()
    cur.close()

    return rst


def query(pool, sql, use_dict=True):

    with pool() as conn:
        return conn_query(conn, sql, use_dict=use_dict)


def new_connection(conn_argkw, conv=None, options=None):

    # useful arg could be added in future.:
    # conn_argkw.init_command

    conv = conv or {}
    options = options or {}

    opt = {
        'autocommit': 1,
    }
    opt.update(options)

    conn = MySQLdb.connect(conv=conv, **conn_argkw)
    for k, v in opt.items():
        conn.query('set {k}={v}'.format(k=k, v=v))

    return conn
