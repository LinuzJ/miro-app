import sqlite3
import json
from flask import g, Flask
from datetime import datetime
import statistics


app = Flask(__name__)


def db_connect():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect('miro_data.db')

    def add_event(event_type, board_id, user, data):
        cur = conn.execute('insert into events (eventType, board,' +
                           'userId, data) values (?, ?, ?, ?);',
                           (event_type, board_id, user, data))
        conn.commit()

    def update_users(board, users):

        ids_list = [x['id'] for x in users]
        # FORMAT: 1,2,3
        user_ids = ','.join(map(lambda x: f"'{x['id']}'", users))

        # Check if user exists and insert
        # user_values = '(' + '),('.join(map(lambda dict: ','.join(dict.values()))) + ')'

        # FORMAT: (id, name, board, 1)
        user_values = map(
            lambda x: '(' + x['id'] + ",'" + x['name'] + "'," + str(board) + ',' + '1)', users)
        user_values = ','.join(user_values)

        # (id,name,board,1),(id,name,board,1)...
        # print(user_values)
        # cur = conn.execute(
        #     f'insert into users(userId, userName, board, isOnline) values {user_values};'
        # )

        # Get users that come online
        # sql = 'select * from users where users.userId in (%s) and users.board = %s and not users.isOnline;'
        # cur = conn.execute(
        #     f'select * from users where users.userId in ({user_values}) and users.board=? and not users.isOnline;', [board]
        # )
        cur = conn.execute(
            'select * from users where users.board=?;', (board)
        )

        rv = cur.fetchall()

        set_online = ','.join([x[0]
                              for x in rv if x[0] in ids_list and x[3] == 0])
        set_offline = ','.join(
            [x[0] for x in rv if x[0] not in ids_list and x[3] == 0])
        print(set_online + ' online')
        print(set_offline + ' offline')
        # Update their values
        # set_online = ','.join(map(lambda x : f"'{x[0]}'", returnvalue)) # users to set to online
        # print(set_online)
        cur = conn.execute(
            f'update users set isOnline = 1 where users.userId in ({set_online}) and users.board=?', (
                board)
        )
        cur = conn.execute(
            f'update users set isOnline = 0 where users.userId not in ({set_online}) and users.board=?', (
                board)
        )
        conn.commit()

        # # Get users that go offline
        # cur = conn.execute(
        #     'select * from users where users.userId not in (?) and users.board =(?) and users.isOnline;', (user_ids, board)
        # )
        # # cur.execute(sql, (user_ids, board))
        # set_offline = ','.join(map(lambda x: f"'{x[0]}'", cur.fetchall())) # users to set to offline
        # print(set_offline)
        # # Update their values
        # # sql = 'update users set isOnline = 0 where users.userId in (%s) and users.board = %s;'
        # cur = conn.execute(
        #     'update users set isOnline = 0 where users.userId in (?) and users.board =(?);', (set_offline, board)
        # )
        # # cur.execute(sql, (set_offline, board))
        # conn.commit()
        # cur.close()
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

        fmt = '%Y-%m-%d %H:%M:%S'
        data_final = {}
        for key, value in board_to_usertime.items():
            data_final[key] = {}
            for key_user, value_times in value.items():
                quer = conn.execute(
                    "SELECT timestamp FROM events WHERE board = ? AND userId = ? AND timestamp >= ? AND timestamp <= ?;",
                    (key, key_user, value_times[0], value_times[1])
                )
                out = quer.fetchall()
                starts = out[::1]
                ends = out[1::1]
                deltas = [(datetime.strptime(
                    end[0], fmt) - datetime.strptime(
                    start[0], fmt)).total_seconds()
                    for start, end in zip(starts, ends)]
                deltas_std = statistics.pstdev(deltas)
                deltas_avg = sum(deltas) / len(deltas)
                data_final[key][key_user] = deltas_avg * deltas_std

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
