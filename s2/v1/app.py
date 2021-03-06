"""
SFU CMPT 756
Sample application---music service.
"""

# Standard library modules
import logging
import os
import sys
import time

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import request
from flask import Response

from prometheus_flask_exporter import PrometheusMetrics

import requests

import simplejson as json

# Local modules
import unique_code

# The unique exercise code
# The EXER environment variable has a value specific to this exercise
ucode = unique_code.exercise_hash(os.getenv('EXER'))

# The application

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Music process')

db = {
    "name": "http://cmpt756db:30002/api/v1/datastore",
    "endpoint": [
        "read",
        "write",
        "delete",
        "read_music",
        "delete_music",
    ]
}
bp = Blueprint('app', __name__)


@bp.route('/health')
@metrics.do_not_track()
def health():
    return Response("", status=200, mimetype="application/json")


@bp.route('/readiness')
@metrics.do_not_track()
def readiness():
    return Response("", status=200, mimetype="application/json")


@bp.route('/list_table', methods=['GET'])
def list_table():
    #for test, list all items in table
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    # list all songs here
    if headers['Authorization'] != 'Bearer A':
        #pass in owner id, list all music under that owner
        payload = {"objtype": "music", "owner": headers['Authorization']}
    else:
        #for testing, list the whole table
        payload = {"objtype": "music"}
    url = db['name'] + '/' + db['endpoint'][3]
    response = requests.get(
        url,
        payload,
        headers={'Authorization': headers['Authorization']})
    return (response.json())


# @bp.route('/', methods=['GET'])
# def list_all():
#     headers = request.headers
#     # check header here
#     if 'Authorization' not in headers:
#         return Response(json.dumps({"error": "missing auth"}),
#                         status=401,
#                         mimetype='application/json')
#     # list all songs here
#     payload = {"objtype": "music"}
#     url = db['name'] + '/' + db['endpoint'][3]
#     response = requests.get(
#         url,
#         payload,
#         headers={'Authorization': headers['Authorization']})
#     return (response.json)   


# @bp.route('/<music_id>/', methods=['GET'])
def get_song(music_id):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    payload = {"objtype": "music", "objkey": music_id}
    url = db['name'] + '/' + db['endpoint'][0]
    response = requests.get(
        url,
        params=payload,
        headers={'Authorization': headers['Authorization']})
    return (response.json())

@bp.route('/<owner>/<music_name>', methods=['GET'])
def get_song_new(owner, music_name):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    payload = {"objtype": "music", "objkey": music_name, "owner": owner}
    url = db['name'] + '/' + db['endpoint'][3]
    response = requests.get(
        url,
        params=payload,
        headers={'Authorization': headers['Authorization']})
    return (response.json())


@bp.route('/', methods=['POST'])
def create_song():
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    try:
        content = request.get_json()
        Artist = content['Artist']
        SongTitle = content['SongTitle']
        Owner = content['Owner']
    except Exception:
        return json.dumps({"message": "error reading arguments"})
    url = db['name'] + '/' + db['endpoint'][1]
    response = requests.post(
        url,
        json={"objtype": "music", "Artist": Artist, "SongTitle": SongTitle, "Owner": Owner},
        headers={'Authorization': headers['Authorization']})
    return (response.json())

# @bp.route('/test_new_db_create', methods=['POST'])
# def create_song_new_db():
#     headers = request.headers
#     # check header here
#     if 'Authorization' not in headers:
#         return Response(json.dumps({"error": "missing auth"}),
#                         status=401,
#                         mimetype='application/json')
#     try:
#         content = request.get_json()
#         Artist = content['Artist']
#         SongTitle = content['SongTitle']
#         Owner = content['Owner']
#     except Exception:
#         return json.dumps({"message": "error reading arguments"})
#     url = db['name'] + '/' + db['endpoint'][1]
#     response = requests.post(
#         url,
#         json={"objtype": "playlist", "Artist": Artist, "SongTitle": SongTitle, "Owner": Owner, "create_time": int(time.time())},
#         headers={'Authorization': headers['Authorization']})
#     return (response.json())



@bp.route('/<music_id>', methods=['DELETE'])
def delete_song(music_id):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    detail = get_song(music_id)
    
    url = db['name'] + '/' + db['endpoint'][2]
    response = requests.delete(
        url,
        params={"objtype": "music", "objkey": music_id},
        headers={'Authorization': headers['Authorization']})

    ret = response.json()
    ret["deleted_song_detail"] = detail
    return (ret)

    
@bp.route('/delete_by_name/<owner>', methods=['DELETE'])
def delete_song_new(owner):

    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')

    try:
        content = request.get_json()
        Artist = content['Artist']
        SongTitle = content['SongTitle']
        # Owner = content['Owner']
    except Exception:
        return json.dumps({"message": "error reading arguments"})
    url = db['name'] + '/' + db['endpoint'][4]
    response = requests.delete(
        url,
        params={"objtype": "music", "objkey": SongTitle, "owner": owner, "artist": Artist},
        headers={'Authorization': headers['Authorization']})
    return (response.json())


@bp.route('/test', methods=['GET'])
def test():
    # This value is for user scp756-221
    if ('7512e8edd61d0e836cc6d39ee1a18ab4d0c8633f854682bf2cace1af12cbc6d0' !=
            ucode):
        raise Exception("Test failed")
    return {}


# All database calls will have this prefix.  Prometheus metric
# calls will not---they will have route '/metrics'.  This is
# the conventional organization.
app.register_blueprint(bp, url_prefix='/api/v1/music/')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("missing port arg 1")
        sys.exit(-1)

    app.logger.error("Unique code: {}".format(ucode))
    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host='0.0.0.0', port=p, threaded=True)
