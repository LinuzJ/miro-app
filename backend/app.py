from flask import Flask, request, jsonify
from db import db_connect
import json


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


@app.route('/add_event', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        db_actions = db_connect()
        add_event = db_actions['add']
        event = request.form['event']
        user = request.form['user']
        if user and event:
            add_event(event, user)
            return 'ok'
        else:
            return 'Wrong data.\nRequired: user, event'
    elif request.method == 'GET':
        return jsonify({
            'message': 'Post a new event',
            'fields': [
                { 'name': 'user', 'type': 'string' },
                { 'name': 'event', 'type': 'string' },
            ],
        })
    else:
        return f'Method "{request.method}" not supported'


if __name__ == '__main__':
    with app.app_context():
        db_connect()['setup']()
    app.run(port=5000, host="0.0.0.0", debug=True)
