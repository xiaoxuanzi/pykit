<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [mysqlconnpool.pool](#mysqlconnpoolpool)
    - [pool](#pool)
    - [pool.query](#poolquery)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


# Name

mysqlconnpool.

Mysql connection pool with MySQLdb in python

#   Status

This library is considered production ready.

#   Synopsis

```python

# create pool
pool = mysqlconnpool.make({
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'mysql',
    'passwd': '123qwe',
})


# get or create a connection and send query on this connection.
# after return, the connection used will be put back to pool.
rst = pool.query('show databases')
# rst = [
#     { 'Database': 'information_schema', },
#     { 'Database': 'mysql', },
#     { 'Database': 'performance_schema', },
#     { 'Database': 'sys', }
# ]


# use with to get a connection, run multiple query on this connection.
# after return, the connection used will be put back to pool.
with pool() as conn:
    conn.query('show tables')
    rst = conn.query('select * from `mysql`.`user`')


# get statistics about pool
stat = pool('stat')
# stat = {'name': 'ip:port',
#         'create': 2,
#         'pool_get': 3,
#         'pool_put': 3,
#         }
```

#   Description

#   Methods

##  mysqlconnpool.pool

**syntax**:
`pool = mysqlconnpool.pool(addr)`

Create a connection pool: `pool`.
Reusable connections are maintained in pool.

**arguments**:
-   `addr`:

    -   To connect with ip and port, `addr` is dictionary that contains:

        ```
        {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'mysql',
            'passwd': '123qwe',
        }
        ```

    -   To connect with `unix_socket`, `addr` is dictionary that contains:

        ```
        {
            'unix_socket': '/tmp/3306.sock',
            'port': 3306,
            'user': 'mysql',
            'passwd': '123qwe',
        }
        ```

**return**:
a function that every time it is called it creates a connection wrapper
instance: `ConnectionWrapper`, which support access with `with`

### pool

**syntax**:
`pool([action])`

**arguments**:
-   `action` = `"get_conn"` or no action is provided:

    get a `ConnectionWrapper` instance or create a new one if pool is empty.
    `ConnectionWrapper` support `with` syntax.

    ```
    with pool() as conn:
        # conn.query('show tables')
    ```

    If there is a exception raised from inside `with` statement, `conn` will
    not be put back but instead, it will be closed.

    **return**:
    `conn` is a MySQLdb connection.

-   `action` = `"stat"`:

    returns a stat dictionary about this pool

    **return**:

    ```
    print pool("stat")

    {'name': 'ip:port',
     'create': 2,
     'pool_get': 3,
     'pool_put': 3,
     }
    ```

### pool.query

**syntax**:
`rst = pool.query(sql, [use_dict=True])`

Get a connection from pool and send `sql` on this connection.
By default it returns query result in dictionary form.

**arguments**:
-   `sql`:
    string sql to query.

-   `use_dict`:
    if specified and is False, `pool.query()` return query result in list
    form.

**return**:
query result in form of list of dictionary,  or list of list(`use_dict`=False).


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
