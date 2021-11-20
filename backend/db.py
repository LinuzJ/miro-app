import sqlite3
import json
from flask import g, Flask

app = Flask(__name__)


def db_connect():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect('miro_data.db')

    def add_event(event_id, event_type, board_id, user, data):
        cur = conn.execute('insert into events (eventId, eventType, board,' +
                           'userId, data) values (?, ?, ?, ?, ?);',
                           (event_id, event_type, board_id, user, data))
        conn.commit()

    def update_users(board, users):

        ids_list = [x['id'] for x in users]
        # FORMAT: 1,2,3
        user_ids = ','.join(map(lambda x: f"'{x['id']}'", users))


        # Check if user exists and insert 
        # user_values = '(' + '),('.join(map(lambda dict: ','.join(dict.values()))) + ')'
        
        # FORMAT: (id, name, board, 1)
        user_values = map(lambda x : '(' + x['id'] + ",'" + x['name'] + "'," + str(board) + ',' + '1)', users)
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
        
        set_online = ','.join([x[0] for x in rv if x[0] in ids_list and x[3] == 0])
        set_offline = ','.join([x[0] for x in rv if x[0] not in ids_list and x[3] == 0])
        print(set_online + ' online')
        print(set_offline + ' offline')
        # Update their values
        # set_online = ','.join(map(lambda x : f"'{x[0]}'", returnvalue)) # users to set to online
        # print(set_online)
        cur = conn.execute(
            f'update users set isOnline = 1 where users.userId in ({set_online}) and users.board=?', (board)
        )
        cur = conn.execute(
            f'update users set isOnline = 0 where users.userId not in ({set_online}) and users.board=?', (board)
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
        rv = cur.fetchall()
        cur.close()
        return rv

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
    eventId text not null,
    eventType text not null,
    board text not null,
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
