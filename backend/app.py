from flask import Flask


app = Flask(__name__)


@app.route('/')
def api():
    return "hello"


if __name__ == '__main__':
    app.run(port=80, host="0.0.0.0", debug=True)
