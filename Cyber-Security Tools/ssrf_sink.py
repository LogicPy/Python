# sink_server.py
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def catch_request():
    print(f"Received request from target server: {request.method} {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Body: {request.get_data()}")
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
