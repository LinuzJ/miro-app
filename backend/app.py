import os
from flask import Flask, request, jsonify
from db import db_connect
import json
from datetime import datetime, timedelta


app = Flask(__name__)


@app.route('/')
def api():
    return "hello"


@app.route('/events')
def all_events():
    db_actions = db_connect()
    get_events = db_actions['get']
    events = get_events()
    if events:
        return jsonify(events)
    else:
        return 'No events found'


@app.route('/events/<event_type>')
def events(event_type):
    db_actions = db_connect()
    get_events = db_actions['get']
    events = get_events(event_type)
    if events:
        return json.loads(events)
    else:
        return 'No events found'


@app.route('/update_users', methods=['GET', 'POST'])
def update_users():
    if request.method == 'POST':
        # Database connection
        db_actions = db_connect()
        add_event = db_actions['update_users']
        # Get data
        data_in = request.get_json()
        # Extract
        board = data_in['data']['boardId']
        users = data_in['data']['users']
        if board and users:
            update_users(board, users)
            return "OK"
        else:
            return 'Wrong data.'
        return "ok"
    elif request.method == "GET":
        return jsonify({
            'message': 'Update users',
            'fields': [
                {'name': 'boardId', 'type': 'string'},
                {'name': 'users', 'type': 'Array'},
            ],
        })
    else:
        return f'Method "{request.method}" not supported'


@app.route('/add_event', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        db_actions = db_connect()
        data = request.get_json(force=True)
        print(data)
        add_event = db_actions['add']
        event_type = data['type']
        board_id = data['board']
        user = data['user']
        data = data.get('data', None)

        if user and event_type and board_id:
            
            add_event(event_type, board_id, user, data)
            return 'ok'
        else:
            return 'Wrong data.\nRequired: user, event'
    elif request.method == 'GET':
        return jsonify({
            'message': 'Post a new event',
            'fields': [
                {'name': 'type', 'type': 'string'},
                {'name': 'board', 'type': 'string'},
                {'name': 'user', 'type': 'string'},
                {'name': 'data', 'type': 'string', 'optional': 'true'},
            ],
        })
    else:
        return f'Method "{request.method}" not supported'

@app.route('/users', methods=['POST', 'GET'])
def users():
    if request.method == 'POST':
        db_actions = db_connect()
        add_event = db_actions['add']
        event_id = request.form['id']
        event_type = request.form['type']
        board_id = request.form['board']
        user = request.form['user']
        data = request.form.get('data', None)
        if user and event_id and event_type and board_id:
            add_event(event_id, event_type, board_id, user, data)
            return 'ok'
        else:
            return 'Wrong data.\nRequired: user, event'
    elif request.method == 'GET':
        return jsonify({
            'message': 'Post a new event',
            'fields': [
                { 'name': 'id', 'type': 'string' },
                { 'name': 'type', 'type': 'string' },
                { 'name': 'board', 'type': 'string' },
                { 'name': 'user', 'type': 'string' },
                { 'name': 'data', 'type': 'string', 'optional': 'true' },
            ],
        })
    else:
        return f'Method "{request.method}" not supported'

# ----------- Advanced AI Analytics endpoints below --------------
@app.route('/time_stats')
def time_stats():
        db_actions = db_connect()
        events = db_actions['user_events']()
        users = {}
        for event_type, user_id, timestamp in events:
            if user_id not in users:
                if event_type == 'USER_JOINED':
                    users[user_id] = { 'joined': timestamp, 'total': timedelta(0) }
            elif 'joined' in users[user_id] and event_type == 'USER_LEFT':
                fmt = '%Y-%m-%d %H:%M:%S'
                interval = datetime.strptime(timestamp, fmt) - datetime.strptime(users[user_id]['joined'], fmt)
                total = users[user_id]['total'] + interval
                users[user_id] = { 'total': total }
            elif 'joined' not in users[user_id] and event_type == 'USER_JOINED':
                    users[user_id] = { 'joined': timestamp, 'total': users[user_id]['total']  }
                    print('add joined')
            else:
                print('Incorrect joined/left event')
        return jsonify({k: v['total'].total_seconds() for k, v in users.items()})




if __name__ == '__main__':
    with app.app_context():
        db_connect()['setup']()
    app.run(port=int(os.environ.get('FLASK_PORT', 80)),
            host="0.0.0.0", debug=True)
