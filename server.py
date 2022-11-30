from flask import Flask, request, jsonify
from flask_executor import Executor
import asyncio
from datetime import datetime
from flask import send_file
import firebase_admin
import pyrebase
import json
from firebase_admin import credentials, auth
from functools import wraps
from werkzeug.exceptions import HTTPException
import requests

from diffusion_utils import DiffusionUtils


app = Flask(__name__)
app.config.from_pyfile("db_config.cfg")


pb = pyrebase.initialize_app(json.load(open('firebase_config.json')))
auth = pb.auth()
db = pb.database()

executor = Executor(app)



def check_token(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        input_json = request.get_json(force=True)
        if not input_json['authorization']:
            return jsonify({'message': 'No token provided'})
        try:
            user = auth.get_account_info(input_json['authorization'])
            request.user = user
            token = input_json['authorization']
        except:
            return jsonify({'message':'Invalid token provided.'})
        return f(*args, **kwargs)
    return wrap



@app.route('/', methods=['GET'])
def home():
    return "<h1>Android Stable Diffusion API</h1><p>This site is a prototype API for making stable diffusion images with android</p>"

@app.route('/make', methods=['POST'])
@check_token
def api_make():
    future = executor.futures.pop(request.user['users'][0]['localId'])
    input_json = request.get_json(force=True) # force=True, above, is necessary if another developer
    print(request.user)
    executor.submit_stored(request.user['users'][0]['localId'], fuser.make, input_json['text'], 1, request.user, token, db_commit_callback)
    return jsonify({'result':'success'})

@app.route('/get-result', methods=['GET', 'POST'])
@check_token
def get_result():
    if not executor.futures.done(request.user['users'][0]['localId']):
        return jsonify({'status': executor.futures._state(request.user['users'][0]['localId'])})
    future = executor.futures.pop(request.user['users'][0]['localId'])
    return jsonify({'status': "done", 'result': future.result()})

@app.route('/get-newest-image', methods=['GET', 'POST'])
@check_token
def get_latest():
    latest = db.child("users").child(request.user['users'][0]['localId']).child("posts").child("image_uri").get()
    print(latest.val())
    return send_file(latest.val(), mimetype='image/png')

@app.route('/api/signup', methods=['POST'])
def signup():
    input_json = request.get_json(force=True)
    email = input_json['email']
    password = input_json['password']
    user = None
    if email is None or password is None:
        return jsonify({'message': 'Error missing email or password'})
    try:
        user = auth.create_user_with_email_and_password(
               email=email,
               password=password
        )
        return jsonify({'message': 'Created'})
    except requests.exceptions.HTTPError as e:
        print(json.loads(e.args[1])['error']['message'], '\n')
        return jsonify({'message': json.loads(e.args[1])['error']['message']})

@app.route('/api/token', methods=['POST'])
def token():
    input_json = request.get_json(force=True)
    email = input_json['email']
    password = input_json['password']
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        jwt = user['idToken']
        return jsonify({'token': jwt})
    except:
        return jsonify({'message': 'There was an error logging in'})

def db_commit_callback(uri, prompt, user, token):
    data = {
        "image_uri": uri,
        "prompt": prompt,
    }
    db.child("users").child(user['users'][0]['localId']).child("posts").set(data)

if __name__ == '__main__':
    global fuser
    fuser = DiffusionUtils()
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

    