from flask import Flask
from flask_cors import CORS
from datetime import timedelta
from os.path import join, dirname
from dotenv import load_dotenv
from lib import parse, httpResponse
import requests
import os
import isodate
import json


# Configure application
app = Flask(__name__)
CORS(app)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Make sure API key is set
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY not set")


# Setting up Google APIs
playlistsAPI = 'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&fields=items/contentDetails/videoId,nextPageToken&key={}&playlistId={}&pageToken='
videoAPI = 'https://www.googleapis.com/youtube/v3/videos?&part=contentDetails&id={}&key={}&fields=items/contentDetails/duration'


@app.route('/v1/playlists/<playlist_id>', methods=['GET'])
def playlistsAPIHandler(playlist_id):
    playlist_id = playlist_id
    next_page = ''  # to store next_page token, empty for first page
    # initializing variables
    count = 0  # to store total number of videos in playlist
    runtime = timedelta(0)  # to store total runtime of a playlist

    while True:
        vid_list = []
        try:
            # make first request to get list of all video_id one page of response
            results = json.loads(requests.get(
                playlistsAPI.format(API_KEY, playlist_id) + next_page).text)

            # add all ids to vid_listf
            for x in results['items']:
                vid_list.append(x['contentDetails']['videoId'])
        except KeyError:
            httpResponse['status'] = 403,
            httpResponse['message'] = 'Forbidden : Permission denied'
            httpResponse["description"] = [results['error']['message']]
            break

        # now vid_list contains list of all videos in playlist one page of response
        url_list = ','.join(vid_list)
        # updating counter
        count += len(vid_list)

        try:
            # now to get the runtimes of all videos in url_list
            op = json.loads(requests.get(
                videoAPI.format(url_list, API_KEY)).text)
            # add all the runtimes to a
            for x in op['items']:
                runtime += isodate.parse_duration(
                    x['contentDetails']['duration'])
        except KeyError:
            httpResponse['status'] = 403,
            httpResponse['message'] = 'Forbidden : Permission denied'
            httpResponse["description"] = [results['error']['message']]
            break

        # if 'nextPageToken' is not in results, it means it is the last page of the response
            # otherwise, or if the count has not yet exceeded 500
        if 'nextPageToken' in results:
            next_page = results['nextPageToken']
        else:
            if count >= 500:
                httpResponse['status'] = 413,
                httpResponse['message'] = 'Content Too Large'
                httpResponse["description"] = 'No of videos limited to 500.'
            httpResponse = {
                "status": 200,
                "message": "OK",
                "description": "Success",
                "data": {
                    "playlist_id": playlist_id,
                    "num_videos": str(count),
                    "total_runtime": {"seconds": runtime.seconds,
                                      "days": runtime.days},
                    "avg_runtime": parse(runtime / count),
                },
            }
            break

    return httpResponse


if __name__ == '__main__':
    app.run(debug=True)
