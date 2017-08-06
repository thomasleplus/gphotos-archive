#!/usr/bin/python

from __future__ import print_function
import datetime
import httplib2
import os
import signal
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from datetime import datetime, timedelta

SCOPES = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.photos.readonly https://picasaweb.google.com/data/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'gphotos-archive'
USER_AGENT = 'Google Photos Archive'

try:
    import argparse
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument('modified_time', nargs=1, help='max modification time in ISO-8601 format (e.g. 2017-15-01T16:45:50)')
    args = parser.parse_args()
except ImportError:
    args = None

def signal_handler(signal, frame):
    print('');
    sys.exit(0)

def get_credentials():
    credential_dir = os.path.join(os.path.expanduser('~'), '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    app_dir = os.path.join(credential_dir, APPLICATION_NAME)
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    token_path = os.path.join(app_dir, 'user_token.json')
    store = Storage(token_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        secret_path = os.path.join(app_dir, 'client_secret.json')
        flow = client.flow_from_clientsecrets(secret_path, SCOPES)
        flow.user_agent = USER_AGENT
        if args:
            credentials = tools.run_flow(flow, store, args)
        else:
            credentials = tools.run(flow, store)
    return credentials

def get_photos(service, modified_time):
    photos = []
    next_page = None
    while True:
        results = service.files().list(q='trashed=false and modifiedTime < \'' + modified_time + '\'', spaces='photos', pageSize=1000, fields="nextPageToken, files(id, name)", pageToken=next_page).execute()
        items = results.get('files', [])
        if not items:
            break
        else:
            photos.extend(items)
            next_page = results.get('nextPageToken')
        if not next_page:
            break
    return photos

def archive_photos(service, photos):
    for photo in photos:
        print(photo['name'])
        service.files().update(fileId = photo['id'], body = { 'trashed' : True }).execute()

def main():
    signal.signal(signal.SIGINT, signal_handler)
    modified_time = args.modified_time[0]
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    photos = get_photos(service, modified_time)
    print('Found {0} photo(s) older than {1}'.format(len(photos), modified_time))
    if photos:
        raw_input('Press Enter to continue...')
        archive_photos(service, photos)

if __name__ == '__main__':
    main()
