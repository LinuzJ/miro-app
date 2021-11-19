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


@app.route('/add_event')
def add():
    if request.method == 'GET':
        db_actions = db_connect()
        add_event = db_actions['add']
        event = request.args.get('event', '')
        user = request.args.get('user', '')
        if user and event:
            add_event(event, user)
    return 'ok'


if __name__ == '__main__':
    with app.app_context():
        db_connect()['setup']()
    app.run(port=80, host="0.0.0.0", debug=True)
