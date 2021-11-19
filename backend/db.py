import sqlite3
from flask import g, Flask

app = Flask(__name__)

def db_connect():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect('miro_data.db')

    def add_event(event_type, user):
        cur = conn.execute('insert into miro_time_tracking (event_type, user) values (?, ?);', (event_type, user))
        conn.commit()

    def get_events(event_type = None):
        if event_type:
            cur = conn.execute('select * from miro_time_tracking where event_type=?;', (event_type))
        else:
            cur = conn.execute('select * from miro_time_tracking;')
        rv = cur.fetchall()
        cur.close()
        return rv

    def setup_table():
        cur = conn.execute('''create table if not exists miro_time_tracking(id integer primary key,
                     event_type text not null, user text not null, timestamp
                     datetime default (datetime('now','localtime')));''')
        conn.commit()
    return { 'add': add_event, 'get': get_events, 'setup': setup_table }

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
