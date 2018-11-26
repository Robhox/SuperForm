import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from flask import current_app
import json

from superform import db

SCOPES = 'https://www.googleapis.com/auth/calendar'
FIELDS_UNAVAILABLE = []

AUTH_FIELDS = False
POST_FORM_VALIDATIONS = {}

CONFIG_FIELDS = ['token']

def run(gcal_publishing,channel_config):

    data = json.loads(channel_config)
    token = data['token']

    #token = {"access_token": "ya29.GlxFBgl-MEOI2NojpWSffhjjcfLPhIT55MNauXbQGD4JZQttj45NUKTtaGEd6GpA1GqRUAAhcDYNnK6s7Dyxpx_50N0EPGiKZJrUcPujhrx2eFaRHO94nGrVDpOlVg", "client_id": "408596117278-fkeuv3g0rdkrdpqsch2i1u18h0lgsakm.apps.googleusercontent.com", "client_secret": "EEZoDYXiIq3q-6zoSUrl9ec8", "refresh_token": "1/OEYHMvVkUmfS9C_CVqYccME6zKCANhB_YcU3SwzA2I3VjsBTr4ecnN1CqSchdDXs", "token_expiry": "2018-10-29T17:15:53Z", "token_uri": "https://www.googleapis.com/oauth2/v3/token", "user_agent": None, "revoke_uri": "https://oauth2.googleapis.com/revoke", "id_token": None, "id_token_jwt": None, "token_response": {"access_token": "ya29.GlxFBgl-MEOI2NojpWSffhjjcfLPhIT55MNauXbQGD4JZQttj45NUKTtaGEd6GpA1GqRUAAhcDYNnK6s7Dyxpx_50N0EPGiKZJrUcPujhrx2eFaRHO94nGrVDpOlVg", "expires_in": 3600, "scope": "https://www.googleapis.com/auth/calendar", "token_type": "Bearer"}, "scopes": ["https://www.googleapis.com/auth/calendar"], "token_info_uri": "https://oauth2.googleapis.com/tokeninfo", "invalid": False, "_class": "OAuth2Credentials", "_module": "oauth2client.client"}
    credentials = None
    try:
        credentials = client.Credentials.new_from_json(json.dumps(token))
    except ValueError:
        pass
    service = build('calendar', 'v3', http=credentials.authorize(Http()))
    template = {}
    template['summary'] = gcal_publishing.title
    template['location'] = gcal_publishing.location
    template['description'] = gcal_publishing.description
    template['start'] = {'dateTime': '{}-{}-{}T{}:00.000'.format(gcal_publishing.date_start.year, gcal_publishing.date_start.month, gcal_publishing.date_start.day,gcal_publishing.hour_start), 'timeZone': 'Europe/Brussels'}
    template['end'] = {'dateTime': '{}-{}-{}T{}:00.000'.format(gcal_publishing.date_end.year, gcal_publishing.date_end.month, gcal_publishing.date_end.day,gcal_publishing.hour_end), 'timeZone': 'Europe/Brussels'}
    template['colorId'] = gcal_publishing.color_id
    #if gcal_publishing.visibility:
    #    template['visibility'] = 'public'
    #else:
    #    template['visibility'] = 'private'
    template['attendees'] = gcal_publishing.guests
    #template['source'] = {"url": gcal_publishing.link_url, "title": 'link'}
    try:
        event = service.events().insert(calendarId='primary', body=template).execute()
    except Exception as e:
        #TODO should add log here
        print(e)
    gcal_publishing.state = 1
    db.session.commit()

# Methods from other groups :

def post_pre_validation(post):
    return 1;

def authenticate(channel_name, publishing_id):
    return 'AlreadyAuthenticated'