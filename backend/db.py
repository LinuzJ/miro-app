import sqlite3
import json
from flask import g, Flask

app = Flask(__name__)


def db_connect():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect('miro_data.db')

    def add_event(event_id, event_type, board_id, user, data):
        cur = conn.execute('insert into events (eventId, eventType, boardId,' +
                           'userId, data) values (?, ?, ?, ?, ?);',
                           (event_id, event_type, board_id, user, data))
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
        rv = cur.fetchall()
        cur.close()
        return rv

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
    eventId text not null,
    eventType text not null,
    boardId text not null,
    userId text not null,
    data text,
    timestamp datetime default (datetime('now','localtime')),
    foreign key (userId) references users(userId)
);
''')
        conn.commit()

    return {'add': add_event, 'get': get_events, 'setup': setup_table, 'update_users': update_users}


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
