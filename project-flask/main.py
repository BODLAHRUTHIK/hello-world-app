from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/hello', methods=['GET'])

def hello():
    if request.method == 'GET':
        d = {'data': "hello world. welcome to the world. yet to test. hey man"}
        return jsonify(d)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6123)
