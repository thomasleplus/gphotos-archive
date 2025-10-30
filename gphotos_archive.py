"""Google Photos archiving script.

This script allows you to bulk archive (trash) photos in Google Photos based on
query criteria. It uses the Google Drive API to access photos and move them to trash.

The script will:
1. Authenticate with Google Drive API using OAuth2
2. Search for photos matching your query (e.g., by modification date)
3. Display the count of matching photos
4. Prompt for confirmation before archiving
5. Move all matching photos to trash

Usage:
    python gphotos_archive.py "modifiedTime < '2017-01-15T16:45:50'"

Requirements:
- client_secret.json file in ~/.credentials/gphotos-archive/
- Google Drive API access enabled
- Required Python packages: google-api-python-client, oauth2client, httplib2
"""

import argparse
import os
import signal
import sys
from argparse import Namespace

import httplib2
from googleapiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

SCOPES = "https://www.googleapis.com/auth/drive \
https://www.googleapis.com/auth/drive.photos.readonly \
https://picasaweb.google.com/data/"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "gphotos-archive"
USER_AGENT = "Google Photos Archive"

try:
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument(
        "query",
        nargs=1,
        help="selection query \
                        (e.g. \"modifiedTime < '2017-15-01T16:45:50'\")",
    )
    ARGS: Namespace | None = parser.parse_args()
except ImportError:
    ARGS = None


def signal_handler(_signal, _frame):
    """Handles SIGINT (Ctrl+C) gracefully.

    Allows the user to interrupt the script execution cleanly.
    """
    print("")
    sys.exit(0)


def get_credentials():
    """Gets user credentials for Google Drive API access.

    Retrieves stored OAuth2 credentials or initiates the OAuth2 flow if
    credentials don't exist or are invalid. Credentials are stored in
    ~/.credentials/gphotos-archive/user_token.json

    Returns:
        OAuth2 credentials object for API authentication.
    """
    credential_dir = os.path.join(os.path.expanduser("~"), ".credentials")
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    app_dir = os.path.join(credential_dir, APPLICATION_NAME)
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    token_path = os.path.join(app_dir, "user_token.json")
    store = Storage(token_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        secret_path = os.path.join(app_dir, "client_secret.json")
        flow = client.flow_from_clientsecrets(secret_path, SCOPES)
        flow.user_agent = USER_AGENT
        if ARGS:
            credentials = tools.run_flow(flow, store, ARGS)
        else:
            credentials = tools.run(flow, store)
    return credentials


def get_photos(service, query):
    """Gets photos matching the specified query from Google Photos.

    Retrieves all photos (paginated) that match the query criteria from the
    Google Photos space using the Drive API. Only non-trashed photos are included.

    Args:
        service: Google Drive API service instance.
        query: Search query string (e.g., "modifiedTime < '2017-01-15T16:45:50'").

    Returns:
        List of photo dictionaries containing 'id' and 'name' fields.
    """
    photos = []
    next_page = None
    while True:
        results = (
            service.files()
            .list(
                q="trashed=false and (" + query + ")",
                spaces="photos",
                pageSize=1000,
                fields="nextPageToken, files(id, name)",
                pageToken=next_page,
            )
            .execute()
        )
        items = results.get("files", [])
        if not items:
            break
        photos.extend(items)
        next_page = results.get("nextPageToken")
        if not next_page:
            break
    return photos


def archive_photos(service, photos):
    """Archives (moves to trash) the specified photos.

    Iterates through the list of photos and moves each one to trash using
    the Drive API. Prints each photo name as it's being archived.

    Args:
        service: Google Drive API service instance.
        photos: List of photo dictionaries with 'id' and 'name' fields.
    """
    for photo in photos:
        print(photo["name"])
        service.files().update(fileId=photo["id"], body={"trashed": True}).execute()


def main():
    """Main function that orchestrates the photo archiving process.

    Coordinates the authentication, photo search, user confirmation,
    and archiving operations. Handles SIGINT for graceful interruption.
    """
    signal.signal(signal.SIGINT, signal_handler)
    query = ARGS.query[0]
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build("drive", "v3", http=http)
    photos = get_photos(service, query)
    print(f'Found {len(photos)} photo(s) matching query "{query}"')
    if photos:
        input("Press Enter to continue...")
        archive_photos(service, photos)


if __name__ == "__main__":
    main()
