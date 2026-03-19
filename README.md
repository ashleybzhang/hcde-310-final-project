# HCDE 310 Final Project: Syncup
Repository for HCDE 310 Final Project

## What it is
Syncup is a group scheduling web app that connects to Google Calendar to find mutual free time for a group of people, then creates the event and sends invites automatically.
Built with Flask and the Google Calendar API for HCDE 310 at the University of Washington.

## What It Does
Planning something with a group usually means a long back-and-forth of "when are you free?" texts. Syncup cuts that out entirely:

You log in with your Google account
You enter the emails of everyone you want to meet with, how long you need, and a date range
Syncup checks everyone's Google Calendar at once using the FreeBusy API
It finds time slots when the whole group is free and shows the top suggestions
You pick a slot, click Schedule, and the event is created with invites sent to everyone automatically


## Project Structure
Final Project
    app.py: Main Flask app — all routes and request handling
    auth.py: Google OAuth 2.0 login logic
    scheduler.py: FreeBusy API calls and free slot algorithm
    requirements.txt: Python dependencies
    credentials.json: Google OAuth credentials (not included — see Setup)
    templates
        index.html: Home page — login button or planning form
        results.html: Suggested time slots page
        scheduled.html: Confirmation page after event is created
    static
        style.css: stylesheet for all pages

## Setup
1. Install dependencies
pip install flask google-auth google-auth-oauthlib google-api-python-client
2. Get Google Calendar API credentials
You need to create your own credentials.json file from Google Cloud Console:

Go to console.cloud.google.com and create a new project
Go to APIs & Services → Library, search for Google Calendar API, and click Enable
Go to APIs & Services → OAuth consent screen, choose External, and fill in your app name and email
Scroll to Test users and add any Google accounts you want to test with
Go to APIs & Services → Credentials → Create Credentials → OAuth Client ID
Choose Web application as the type
Under Authorized redirect URIs, add: http://localhost:5000/oauth2callback
Click Create, then download the JSON file
Rename it to credentials.json and place it in the project root folder

3. Run the app
python app.py
Open your browser and go to http://127.0.0.1:5000

## How to Use

Click Sign in with Google and log in with your Google account
Enter participant emails separated by commas (up to 5 people)
Choose a meeting duration and date range
Click Find Times
Pick a suggested slot and click Schedule this
The event will appear in your Google Calendar and invites will be sent to all participants


Note: The app checks free/busy data for all participants. For this to work, each participant's Google Calendar must have free/busy sharing enabled (this is the default for most accounts). If a participant's calendar returns a "not found" error, the app treats them as having no busy blocks.


## Technologies Used

Python / Flask — backend web framework
Google Calendar API — free/busy lookups and event creation
Google OAuth 2.0 — user authentication via google-auth-oauthlib
HTML / CSS — frontend templates using Flask's Jinja2 templating


## Known Limitations

Only checks availability between 9 AM and 6 PM
Date range is limited to 14 days for performance
Maximum of 5 participants
The app is in development mode and must be run locally — it is not deployed to a public server
Participants whose calendars are set to private will show as having no busy blocks


## Notes on API Keys
credentials.json is not included in this repository. You must generate your own by following the Setup instructions above. Never commit your credentials file to a public GitHub repository.
