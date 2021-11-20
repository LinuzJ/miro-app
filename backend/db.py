import sqlite3
import json
from flask import g, Flask
from datetime import datetime
import statistics

from flask.helpers import total_seconds


app = Flask(__name__)


def db_connect():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect('miro_data.db')

    def add_event(event_type, board_id, user, data):
        # cur = conn.execute('insert into events (eventType, board,' +
        #                    'userId, data) values (?, ?, ?, ?);',
        #                    (event_type, board_id, user, data))
        # conn.commit()
        print('add event')

    def update_users(board, users):
        # TODO get who this inserts, return real values
        ids_list = [x['id'] for x in users]
        print(ids_list)
        # FORMAT: 1,2,3
        user_ids = ','.join(map(lambda x: f"'{x['id']}'", users))

        # Check if user exists and insert
        # user_values = '(' + '),('.join(map(lambda dict: ','.join(dict.values()))) + ')'

        # FORMAT: (id, name, board, 1)

        # (id,name,board,1),(id,name,board,1)...
        # print(user_values)
        # cur = conn.execute(
        #     f'insert into users(userId, userName, board, isOnline) values {user_values};'
        # )
        user_values_list = [(x['id'], x['name'], board, 1) for x in users]
        print(user_values_list)
        cur = conn.executemany(
            'insert or replace into users(userId, userName, board, isOnline) values (?, ?, ?, ?);', user_values_list
        )

        cur = conn.execute(
            'select * from users where users.board=?;', (board)
        )

        rv = cur.fetchall()
        # print(rv)
        set_online = ','.join(
            [x[0] for x in rv if x[0] in ids_list and x[3] == 0])
        set_offline = ','.join(
            [x[0] for x in rv if x[0] not in ids_list and x[3] == 1])

        for user in set_online:
            cur = conn.execute(
                'update users set isOnline = 1 where users.userId =? and users.board=?;', (
                    user, board)
            )
        for user in set_offline:
            cur = conn.execute(
                'update users set isOnline = 0 where users.userId =? and users.board=?;', (
                    user, board)
            )
        conn.commit()

        return ('ok', False)

    def get_events(event_type=None):
        if event_type:
            cur = conn.execute(
                'select * from events where eventType=(?);', (event_type))
        else:
            cur = conn.execute('select * from events;')
        return cur.fetchall()

    def user_events():
        cur = conn.execute("select eventType, userId, timestamp from events where eventType='USER_JOINED' " +
                           "or eventType='USER_LEFT' order by " +
                           "timestamp;")
        return cur.fetchall()

    def user_activity():
        cur = conn.execute(
            "SELECT COUNT(events.userId) FROM (events INNER JOIN users ON events.userId = users.userId) GROUP BY events.board, events.userId")

        return cur.fetchall()

    def add_manager(board, usr):
        conn.execute(
            'INSERT INTO managers (board, user) VALUES (?, ?);', (board, usr))
        conn.commit()

    def del_manager(board, usr):
        conn.execute(
            'DELETE FROM managers WHERE managers.board = ? AND managers.user = ?;',
            (board, usr)
        )
        conn.commit()

    def get_managers(board=None):
        if board:
            curr = conn.execute(
                'SELECT * FROM managers WHERE board = ?;', (board)
            )
        else:
            curr = conn.execute(
                'SELECT * FROM managers;'
            )
        re = curr.fetchall()
        curr.close()
        print(re)
        return re

    def stats_productivity():
        cur = conn.execute(
            "SELECT userId, board, eventType, timestamp FROM events WHERE eventType='USER_JOINED' OR eventType='USER_LEFT';"
        )
        join_events = cur.fetchall()
        # Set of users
        users = set(map(lambda x: x[0], join_events))
        # list if user in and out times
        timestamps_per_users = [[(y[0], y[1], y[3])
                                 for y in join_events if y[0] == x] for x in users]
        # COnvert to dict {user -> (in, out)}

        # user_to_time = {x[0][0]: (x[0][2], x[1][2]) for x in timestamps_per_users}

        board_to_usertime = {}
        for x in timestamps_per_users:
            b = x[0][1]  # board
            u = x[0][0]  # user
            if b in board_to_usertime:
                board_to_usertime[b][u] = (x[0][2], x[1][2])
            else:
                board_to_usertime[b] = {}  # Init dict
                board_to_usertime[b][u] = (x[0][2], x[1][2])

        def timedif(e, s):
            fmt = '%Y-%m-%d %H:%M:%S'
            return (datetime.strptime(
                    e, fmt) - datetime.strptime(
                    s, fmt)).total_seconds()

        data_final = {}
        for key, value in board_to_usertime.items():
            data_final[key] = {}
            for key_user, value_times in value.items():
                quer = conn.execute(
                    "SELECT timestamp FROM events WHERE board = ? AND userId = ? AND timestamp >= ? AND timestamp <= ?;",
                    (key, key_user, value_times[0], value_times[1])
                )
                out = quer.fetchall()
                total_time = timedif(out[-1][0], out[0][0])
                starts = out[::1]
                ends = out[1::1]
                deltas = [timedif(end[0], start[0])
                          for start, end in zip(starts, ends)]
                deltas_std = statistics.pstdev(deltas)
                deltas_avg = (sum(deltas) / len(deltas)) / total_time
                data_final[key][key_user] = 1 / (deltas_avg * deltas_std)

        return data_final

    def setup_table():
        cur = conn.executescript('''
create table if not exists users(
    userId text not null,
    userName text,
    board text,
    isOnline integer default (1),
    primary key (userId, board)
);
create table if not exists events(
    id integer primary key,
    eventType text not null,
    board text not null,
    userId text not null,
    data text,
    timestamp datetime default (datetime('now','localtime')),
    foreign key (userId) references users(userId)
);
CREATE TABLE IF NOT EXISTS managers(
    ID INTEGER PRIMARY KEY,
    board TEXT NOT NULL,
    user TEXT NOT NULL
);
''')
        conn.commit()
    return {
        'add': add_event,
        'get': get_events,
        'setup': setup_table,
        'user_events': user_events,
        'update_users': update_users,
        'activity': user_activity,
        'add_manager': add_manager,
        'del_manager': del_manager,
        'get_managers': get_managers,
        'stats_prod': stats_productivity
    }


@ app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
