"""
SFU CMPT 756
Sample application---music service.
"""

# Standard library modules
import logging
import os
import sys

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import request
from flask import Response

from prometheus_flask_exporter import PrometheusMetrics

import requests

import simplejson as json
import time

# Local modules
import unique_code

# The unique exercise code
# The EXER environment variable has a value specific to this exercise
# ucode = unique_code.exercise_hash(os.getenv('EXER'))

# The application

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Playlist process')

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

@bp.route('/show_playlist', methods=['GET'])
def show_playlist():
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    # list all songs here
    if headers['Authorization'] != 'Bearer A':
        #pass in owner id, list all music under that owner
        payload = {"objtype": "PlayList"}
    else:
        #for testing, list the whole table
        payload = {"objtype": "PlayList"}
    url = db['name'] + '/' + db['endpoint'][3]
    response = requests.get(
        url,
        payload,
        headers={'Authorization': headers['Authorization']})
    return (response.json())

@bp.route('/read', methods=['GET'])
def get_song():
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


    payload = {"objtype": "playlist", "objkey": SongTitle, "artist": Artist, "owner": Owner}
    url = db['name'] + '/' + db['endpoint'][3]
    response = requests.get(
        url,
        params=payload,
        headers={'Authorization': headers['Authorization']})
    return (response.json())

@bp.route('/play/<owner>/<music_name>', methods=['GET'])
def play_music(owner, music_name):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')

    #check if music in play list:    
    payload = {"objtype": "Playlist", "owner": headers['Authorization']}
    url = db['name'] + '/' + db['endpoint'][3]
    response = requests.get(
        url,
        payload,
        headers={'Authorization': headers['Authorization']})

    items = response.json()
    if 'Count' not in items or items['Count'] == 0:
        return (response.json())
    else:
        if music_name != "NONE":
            #same as read
            # payload = {"objtype": "Playlist", "objkey": music_name, "owner": headers['Authorization'], "create_time": 0}
            payload = {"objtype": "Playlist", "objkey": music_name, "owner": owner}
            url = db['name'] + '/' + db['endpoint'][3]
            response = requests.get(
                url,
                params=payload,
                headers={'Authorization': headers['Authorization']})
            return (response.json())

        else:
            payload = {"objtype": "Playlist", "owner": headers['Authorization'], "create_time": 0}
            # play from begining
            url = db['name'] + "/next"
            response = requests.get(
                url,
                payload,
                headers={'Authorization': headers['Authorization']})
            items = response.json()
    
    return (response.json())

@bp.route('/next/<owner>/<create_time>', methods=['GET'])
def next_music(owner, create_time):
    headers = request.headers
    create_time = int(create_time)
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')

    #check if music in play list:
    payload = {"objtype": "Playlist", "owner": headers['Authorization'], "create_time": create_time}
    url = db['name'] + '/' + db['endpoint'][3]
    response = requests.get(
        url,
        payload,
        headers={'Authorization': headers['Authorization']})

    items = response.json()
    if 'Count' not in items or items['Count'] == 0:
        return (response.json())
    else:
        # print("count: " + str(items['Count']))
        # try play newer one
        url = db['name'] + "/next"
        response_ = requests.get(
            url,
            payload,
            headers={'Authorization': headers['Authorization']})
        items_ = response_.json()
        
        if 'Count' not in items_  or items_['Count'] == 0:        
            # otherwise play from begining
            url = db['name'] + "/next"
            payload = {"objtype": "Playlist", "owner": headers['Authorization'], "create_time": 0}
            response__ = requests.get(
                url,
                payload,
                headers={'Authorization': headers['Authorization']})
            ret = response__.json()
            ret["test_the_last_query"] = str(items_)
            return (ret)
        else:
            # print("count: " + str(items_['Count']))
            return (response_.json())
    
    return (response.json())

@bp.route('/prev/<owner>/<create_time>', methods=['GET'])
def prev_music(owner, create_time):
    headers = request.headers
    create_time = int(create_time)
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')

    #check if music in play list:
    payload = {"objtype": "Playlist", "owner": headers['Authorization'], "create_time": create_time}
    url = db['name'] + '/' + db['endpoint'][3]
    response = requests.get(
        url,
        payload,
        headers={'Authorization': headers['Authorization']})

    items = response.json()
    if 'Count' not in items or items['Count'] == 0:
        return (response.json())
    else:
        # print("count: " + str(items['Count']))
        # try play newer one
        url = db['name'] + "/prev"
        response_ = requests.get(
            url,
            payload,
            headers={'Authorization': headers['Authorization']})
        items_ = response_.json()
        
        if 'Count' not in items_  or items_['Count'] == 0:        
            # otherwise play from begining
            url = db['name'] + "/next"
            payload = {"objtype": "Playlist", "owner": headers['Authorization'], "create_time": 0}
            response__ = requests.get(
                url,
                payload,
                headers={'Authorization': headers['Authorization']})
            ret = response__.json()
            ret["test_the_last_query"] = str(items_)
            return (ret)
        else:
            # print("count: " + str(items_['Count']))
            return (response_.json())
    
    return (response.json())

@bp.route('/add_music_to_playlist', methods=['POST'])
def add_music_to_playlist():
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

    #read from music_list first
    payload = {"objtype": "music", "objkey": SongTitle, "Artist": Artist, "owner": Owner}
    url = db['name'] + '/' + db['endpoint'][3]
    response = requests.get(
        url,
        params=payload,
        headers={'Authorization': headers['Authorization']})
    
    items = response.json()        
    if 'Count' not in items  or items['Count'] == 0:  
        ret = response.json()
        ret['Error Message'] = "Can only add music existed in music list to play list!"
        return (ret)
    else:
        url = db['name'] + '/' + db['endpoint'][1]
        response = requests.post(
            url,
            json={"objtype": "playlist", "Artist": Artist, "SongTitle": SongTitle, "Owner": Owner, "create_time": int(time.time())},
            headers={'Authorization': headers['Authorization']})
        return (response.json())
    return (response.json())


@bp.route('/<music_id>', methods=['DELETE'])
def delete_song(music_id):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    # detail = get_song(music_id)
    
    url = db['name'] + '/' + db['endpoint'][2]
    response = requests.delete(
        url,
        params={"objtype": "playlist", "objkey": music_id},
        headers={'Authorization': headers['Authorization']})

    # ret = response.json()
    # ret["deleted_song_detail"] = detail
    return ( response.json())

    
@bp.route('/delete_by_name/<owner>', methods=['DELETE'])
def delete_song_by_name(owner):

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
        params={"objtype": "playlist", "objkey": SongTitle, "owner": owner, "artist": Artist},
        headers={'Authorization': headers['Authorization']})
    return (response.json())


@bp.route('/health')
@metrics.do_not_track()
def health():
    return Response("", status=200, mimetype="application/json")


@bp.route('/readiness')
@metrics.do_not_track()
def readiness():
    return Response("", status=200, mimetype="application/json")

app.register_blueprint(bp, url_prefix='/api/v1/playlist/')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("Usage: app.py <service-port>")
        sys.exit(-1)

    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host='0.0.0.0', port=p, threaded=True)
