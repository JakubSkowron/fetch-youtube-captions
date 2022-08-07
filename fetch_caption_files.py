#!/usr/bin/env python3
import urllib.request
import urllib.parse
import sys
import json
import os

languageCode = 'fr'

# YouTube video subtitles, returns list of JSON objects


def get_subtitle_tracks(video_url):
    # Parse video page to find subltitles URL
    subtitle_url = None
    with urllib.request.urlopen(video_url) as response:
        data = response.read()
        pos = data.find(b'"playerCaptionsTracklistRenderer"')
        if pos == -1:
            print("No captions found")
            return
        pos = data.find(b':', pos)
        pos += 1

        # Parse until first JSON error
        track_list = None

        def hook(obj):
            nonlocal track_list
            track_list = obj
            return obj

        try:
            json.loads(data[pos:], object_hook=hook)
        except json.JSONDecodeError:
            pass

        return track_list['captionTracks']


def download_subtitle(video_url):
    tracks = get_subtitle_tracks(video_url)
    if not tracks:
        return
    tracks = [track for track in tracks if track['languageCode'] == languageCode]

    if not tracks:
        print("No", languageCode, "captions found")
        return

    def isASR(track):
        return 'kind' in track and track['kind'] == 'asr'

    # Prioritise not Atomated Speech Recognition
    track = next((t for t in tracks if not isASR(t)), tracks[0])
    subtitle_url = track['baseUrl']

    with urllib.request.urlopen(subtitle_url) as response:
        xml_data = response.read()

    # Save it in current directory
    filename = urllib.parse.urlsplit(video_url).query + '.xml'
    with open(os.path.join("xml", filename), 'wb') as f:
        f.write(xml_data)

    print("Written", filename,
          track['languageCode'], "ASR" if isASR(track) else "")


os.makedirs("xml", exist_ok=True)
for video_url in sys.argv[1:]:
    download_subtitle(video_url)
