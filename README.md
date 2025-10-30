# Google Photos Archive

A Python tool to bulk archive (trash) photos in Google Photos based on custom query criteria.

## Overview

This script allows you to search and archive photos in Google Photos using the Google Drive API. It's useful for managing large photo libraries and removing photos that match specific criteria (such as date ranges).

**Important:** This script moves photos to trash, not permanent deletion. Photos can be restored from trash within 60 days.

## What It Does

The script performs the following operations:

1. **Authenticates** with Google using OAuth2
2. **Searches** for photos matching your specified query criteria
3. **Displays** the count of matching photos
4. **Prompts** for user confirmation before taking action
5. **Archives** (moves to trash) all confirmed photos

## Requirements

### Prerequisites

- Python 3.x
- Google account with Google Photos
- Google Cloud project with Drive API enabled

### Python Packages

Install required dependencies:

```bash
pip install google-api-python-client oauth2client httplib2
```

## Setup

### 1. Enable Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API for your project
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials file

### 2. Configure Credentials

Place your downloaded `client_secret.json` file in:

```bash
~/.credentials/gphotos-archive/client_secret.json
```

The script will create this directory structure automatically, but you need to place the `client_secret.json` file there manually.

## Usage

### Basic Syntax

```bash
python gphotos_archive.py "<query>"
```

### Query Examples

Archive photos modified before a specific date:

```bash
python gphotos_archive.py "modifiedTime < '2017-01-15T16:45:50'"
```

Archive photos modified after a specific date:

```bash
python gphotos_archive.py "modifiedTime > '2020-12-31T23:59:59'"
```

Archive photos within a date range:

```bash
python gphotos_archive.py "modifiedTime > '2015-01-01T00:00:00' and modifiedTime < '2016-01-01T00:00:00'"
```

### Query Operators

The query syntax follows Google Drive API search parameters:

- `<` - Less than
- `<=` - Less than or equal to
- `>` - Greater than
- `>=` - Greater than or equal to
- `=` - Equal to
- `and` - Logical AND
- `or` - Logical OR

Date format: `YYYY-MM-DDTHH:MM:SS`

## First Run

On first execution, the script will:

1. Open your default web browser
2. Ask you to authorize the application
3. Save credentials to `~/.credentials/gphotos-archive/user_token.json`

Subsequent runs will use the saved credentials automatically.

## Safety Features

- **Confirmation prompt**: The script always shows the count of matching photos and waits for Enter before archiving
- **Ctrl+C support**: You can interrupt the script at any time with Ctrl+C
- **Trash, not delete**: Photos are moved to trash and can be recovered within 60 days

## Troubleshooting

### Authentication Errors

If you encounter authentication issues:

1. Delete `~/.credentials/gphotos-archive/user_token.json`
2. Run the script again to re-authorize

### No Photos Found

- Verify your query syntax
- Check that photos exist in Google Photos matching your criteria
- Ensure the Drive API has access to your Google Photos

## Limitations

- Only works with photos stored in Google Photos
- Requires internet connection
- Subject to Google Drive API rate limits
- Does not permanently delete photos (only moves to trash)

## License

See LICENSE file for details.
