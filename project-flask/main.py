from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/hello', methods=['GET'])

def hello():
    if request.method == 'GET':
        d = {'data': "hello world"}
        return jsonify(d)
    
print('tesig')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6123)
