import sqlite3
import json
from flask import g, Flask
from datetime import datetime, time, timedelta
from itertools import groupby
import statistics
from flask.helpers import total_seconds


app = Flask(__name__)


def db_connect():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect('miro_data.db')

    def add_event(event_type, board_id, user, data):
        print(event_type, board_id, user, data)
        cur = conn.execute('insert into events (eventType, board,' +
                           'userId, data) values (?, ?, ?, ?);',
                           (event_type, board_id, user, json.dumps(data)))
        conn.commit()

    # Returns a dict {userId: joined_boolean}
    def update_users(board, users):
        ids_list = [x['id'] for x in users]
        user_values_list = [(x['id'], x['name'], board, 1) for x in users]

        # Hacky shit ahead
        # If users online is = 1 and users id list length = 1
        #   set old online user offline with timestamp (latest event)

        count_online = conn.execute(
            'select sum(isOnline) from users where board =(?);', (board,)
        ).fetchall()[0][0]

        if len(ids_list) == 1 and count_online == 1:
            # get latest event for old user
            old_user = conn.execute(
                'select userId from users where isOnline and board =(?);', (
                    board,)
            ).fetchall()[0][0]
            latest_timestamp = conn.execute(
                'select timestamp from events where userId = (?) order by timestamp desc limit 1;', (
                    old_user,)
            ).fetchall()[0][0]

            # Insert USER_LEFT event into DB
            conn.execute(
                'insert into events(eventType, board, userId, data, timestamp) values (?, ?, ?, ?, ?);',
                ('USER_LEFT', board, old_user, None, latest_timestamp)
            )

        # select from online users where user not in DB
        change_dict = {}
        for user in user_values_list:
            rv = conn.execute(
                'with user(userId, userName, board) as (values (?, ?, ?)) select user.userId, user.userName from user left join users on user.userId = users.userId where users.userId is null or users.board <> user.board;', (
                    user[0], user[1], user[2])
            ).fetchall()

            if rv:
                conn.execute(
                    'insert or replace into users(userId, userName, board) values (?, ?, ?);', (
                        user[0], user[1], board)
                )
                conn.commit()
                change_dict[user[0]] = True

        cur = conn.execute(
            'select * from users where users.board=(?);', (board,)
        )
        rv = cur.fetchall()

        set_online = [x[0] for x in rv if x[0] in ids_list and x[3] == 0]
        set_offline = [x[0] for x in rv if x[0] not in ids_list and x[3] == 1]


        # USER JOINED
        for userId in set_online:
            cur = conn.execute(
                'update users set isOnline = 1 where users.userId =(?) and users.board=(?) and users.isOnline = 0;', (
                    userId, board)
            )
            if cur.rowcount > 0:
                change_dict[userId] = True
        # USER LEFT 
        for userId in set_offline:
            cur = conn.execute(
                'update users set isOnline = 0 where users.userId =(?) and users.board=(?) and users.isOnline = 1;', (
                    userId, board)
            )
            if cur.rowcount > 0:
                change_dict[userId] = False

        conn.commit()
        return change_dict
        # to_online_dict = {user: 'USER_JOINED' for user in set_online}
        # to_offline_dict = {user: 'USER_LEFT' for user in set_offline}

        # return ({**insert_dict, **to_online_dict, **to_offline_dict})

    def get_events(event_type=None):
        if event_type:
            cur = conn.execute(
                'select * from events where eventType=(?);', (event_type))
        else:
            cur = conn.execute('select * from events;')
        return cur.fetchall()

    def user_events():
        cur = conn.execute("select eventType, board, userId, timestamp from events where eventType='USER_JOINED' " +
                           "or eventType='USER_LEFT' order by " +
                           "timestamp;")
        return cur.fetchall()

    def user_activity():
        cur = conn.execute(
            "SELECT COUNT(events.userId) FROM (events INNER JOIN users ON events.userId = users.userId) GROUP BY events.board, events.userId")

        return cur.fetchall()

    def get_username():
        cur = conn.execute(
            'select userId, userName from users;'
        )
        return {x[0]: x[1] for x in cur}

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

    def get_managers(board):
        try:
            if board:
                curr = conn.execute(
                    'SELECT userId, userName FROM (managers INNER JOIN users ON managers.user = users.userId) WHERE managers.board = (?);', (
                        board,)
                )
            else:
                curr = conn.execute(
                    'SELECT * FROM (managers INNER JOIN users ON managers.user = users.userId);'
                )
            re = curr.fetchall()
            curr.close()
            print(re)
            if len(re) > 0:
                return [{"id": x[0], "name": x[1]} for x in re]
            else:
                return []
        except Exception as e:
            return f'Error is: {e}'

    def stats_productivity(board):
        cur = conn.execute(
            "SELECT userName, events.board, eventType, timestamp FROM (events INNER JOIN users ON events.userId = users.userId) WHERE (events.eventType='USER_JOINED' OR events.eventType='USER_LEFT') AND events.board = (?);",
            (board,)
        )
        join_events = cur.fetchall()
        # Set of users
        users = set(map(lambda x: x[0], join_events))
        # list if user in and out times
        # (name, board, timestamp)
        timestamps_per_users = [[(y[0], y[1], y[3])
                                 for y in join_events if y[0] == x] for x in users]

        # Convert to dict {user -> (in, out)}
        board_to_usertime = {}
        for x in timestamps_per_users:

            b = x[0][1]  # board
            u = x[0][0]  # user
            # Check if out exists
            if len(x) > 1:
                if b in board_to_usertime:
                    board_to_usertime[b][u] = (x[0][2], x[1][2])
                else:
                    board_to_usertime[b] = {}  # Init dict
                    board_to_usertime[b][u] = (x[0][2], x[1][2])
            else:
                fmt = '%Y-%m-%d %H:%M:%S'
                now = datetime.now()
                time_now = now.strftime(fmt)
                if b in board_to_usertime:
                    board_to_usertime[b][u] = (x[0][2], time_now)
                else:
                    board_to_usertime[b] = {}  # Init dict
                    board_to_usertime[b][u] = (x[0][2], time_now)

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
                if len(out) > 2:
                    total_time = timedif(out[-1][0], out[0][0])
                    starts = out[::1]
                    ends = out[1::1]
                    deltas = [timedif(end[0], start[0])
                              for start, end in zip(starts, ends)]
                    deltas_std = statistics.pstdev(deltas) * 1000
                    deltas_avg = (sum(deltas) / len(deltas)) * 1000
                    data_final[key][key_user] = 1 / (deltas_avg * deltas_std)
                else:
                    data_final[key][key_user] = 0

        return data_final

    def selection_insight(board, days_to_subtract):
        d = datetime.today() - timedelta(days=days_to_subtract)
        curr = conn.execute(
            'SELECT DISTINCT userId, data FROM events WHERE board = (?) AND data <> "null" AND data IS NOT NULL AND timestamp > (?);',
            (board, d)
        )
        fetched = curr.fetchall()
        # Tranform into tuple with (userId, objectId, objectType)
        availible_data = []
        for x in fetched:
            id = json.loads(x[1])
            if 'objectType' not in id:
                continue
            availible_data.append(
                (x[0], id['objectId'], id['objectType'])
            )

        # Groupby objectId and collect length and tems of each group

        groups = {}
        for key, group in groupby(availible_data, lambda x: x[1]):
            y = list(group)
            print(key, y)
            if len(y) >= 3:
                groups[key] = [(z[0], z[-1]) for z in y][0:3]

        key = list(groups.keys())[0]
        data_ = groups[key]
        object_ = data_[0][-1]
        names = []
        usernames = get_username()
        for i in data_:
            names.append(usernames.get(i[0], 'No username'))

        return (key, object_, names)

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
        'stats_prod': stats_productivity,
        'get_username': get_username,
        'select_insight': selection_insight,
    }


@ app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
