import sqlite3
import json
from flask import g, Flask

app = Flask(__name__)


def db_connect():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect('miro_data.db')

    def add_event(event_type, board_id, user, data):
        cur = conn.execute('insert into events (eventType, boardId,' +
                           'userId, data) values (?, ?, ?, ?);',
                           (event_type, board_id, user, data))
        conn.commit()

    def update_users(boardId, users):
        user_ids = ','.join(map(lambda x: x['id']), users)
        cur = conn.execute(
            f'select * from user where users.id in ({user_ids}) and users.boardId = boardId;')
        rv = cur.fetchall()
        cur.close()
        return rv

    def get_events(event_type=None):
        if event_type:
            cur = conn.execute(
                'select * from events where eventType=?;', (event_type))
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
            "SELECT COUNT(events.userId) FROM (events INNER JOIN users ON events.userId = users.userId) GROUP BY boardId, events.userId")

        return cur.fetchall()

    def add_manager(board, usr):
        conn.execute(
            'INSERT INTO managers (board, user) VALUES (?, ?);', (board, usr))
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

    def setup_table():
        cur = conn.executescript('''
create table if not exists users(
    id integer primary key,
    userId text not null,
    userName text,
    isOnline integer default (1)
);
create table if not exists events(
    id integer primary key,
    eventType text not null,
    boardId text not null,
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
        'get_managers': get_managers
    }


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
