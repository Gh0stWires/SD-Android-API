from flask import Flask, request, jsonify
from flask_executor import Executor
from flask_sqlalchemy import SQLAlchemy
import asyncio
from datetime import datetime
from flask import send_file

from diffusion_utils import DiffusionUtils


app = Flask(__name__)
app.config.from_pyfile("db_config.cfg")

db = SQLAlchemy()
executor = Executor(app)
db.init_app(app)



@app.route('/', methods=['GET'])
def home():
    return "<h1>Android Stable Diffusion API</h1><p>This site is a prototype API for making stable diffusion images with android</p>"

@app.route('/make', methods=['POST'])
def api_make():
    input_json = request.get_json(force=True) # force=True, above, is necessary if another developer
    executor.submit_stored('draw', fuser.make, input_json['text'], 1, db_commit_callback)
    return jsonify({'result':'success'})

@app.route('/get-result', methods=['GET'])
def get_result():
    if not executor.futures.done('draw'):
        return jsonify({'status': executor.futures._state('draw')})
    future = executor.futures.pop('draw')
    return jsonify({'status': "done", 'result': future.result()})

@app.route('/get-newest-image')
def get_latest():
    latest = Image.query.order_by(Image.id.desc()).first().uri
    return send_file(latest, mimetype='image/png')


def db_commit_callback(uri, prompt):
    db.session.add(Image(uri=uri, prompt=prompt))
    db.session.commit()

class Image(db.Model):
    __tablename__ = "image"
    id = db.Column("image_id", db.Integer, primary_key=True)
    title = db.Column(db.String(600))
    uri = db.Column(db.String)
    pub_date = db.Column(db.DateTime)

    def __init__(self, prompt, uri):
        self.title = prompt
        self.uri = uri
        self.pub_date = datetime.utcnow()

    def __repr__(self):
        return f"Image(id={self.id!r}, uri={self.uri!r})"

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    global fuser
    fuser = DiffusionUtils()
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

    