'''
assumptions:
  - credit one, the leading provider of identity management is a division of capital one (e.g. https://capitalone.com/creditone)
  - user already has an account with capital one (they've been verified id, passport, credit, ...)
  - participating banks, institutions, ... realize credit one the leading
    provider of identity management
  - all third parties below, are authorized (they have client id/secret) partners with credit one


scenarios:
  - student wants to open account at bank a
    - bank a doesn't want to collect information manually from user
    - they are partner with credit one
    - bank a will use signup feature of credit one
      - user is directed to capital one site
      - user logs in and approves
      - user is redirected back to partner site w/ personal info
    - bank a uses personal info to create account

  - student wants to open account at bank b
    - bank b will collect person information from each user, but does not
      have the capacity to handle due diligence to verify user
    - bank b will use verify feature of credit one
      - user is directed to capital one site
      - user logs in and approves (allows the verification)
      - bank b gets salt to hash information on it's end before sending to capital one
      - bank b then sends user info to be verified
    - verification is passed, bank b creates account for user

questions:
  - for scope of this hackathon, do we say we are the devex api or are we the proxy between
  a partner site and the devex api

'''
import os
import requests

from flask import Flask, flash, render_template, redirect, request, session, url_for
from requests_oauthlib import OAuth2Session


app = Flask(__name__, static_folder='static', instance_relative_config=True)

# load default config and secrets
app.config.from_object('config')
app.config.from_pyfile('config.py') # instance/config.py
os.environ['OAUTHLIB_INSECURE_TRANSPORT']='1' # for testing, we use non-HTTPS

SESSKEY_DEXEX_STATE='devex'

def create_oauth():
    return OAuth2Session(app.config['OAUTH_DEVEX_ID'],
        scope=['openid','signin'],
        state=(session.get(SESSKEY_DEXEX_STATE) if SESSKEY_DEXEX_STATE in session else None),
        redirect_uri='http://localhost:5000/signin/complete')


@app.route('/')
def home():
    if 'user' not in session:
        return render_template('signin.html')
    else:
        return render_template('home.html')

@app.route('/signin')
def signin():
    oauth_session = create_oauth()
    authorization_url, oauth_state = oauth_session.authorization_url('http://api.devexhacks.com/oauth2/authorize')
    session[SESSKEY_DEXEX_STATE] = oauth_state
    return redirect(authorization_url)


@app.route('/signin/complete')
def signin_complete():
    if not SESSKEY_DEXEX_STATE in session or \
            not all(k in request.args for k in ('code', 'state')) or \
            request.args['state'] != session.get(SESSKEY_DEXEX_STATE):
        return abort(401)

    oauth_session = create_oauth()
    oauth_token = oauth_session.fetch_token('http://api.devexhacks.com/oauth2/token',
        client_secret=app.config['OAUTH_DEVEX_SECRET'],
        authorization_response=request.url)

    if 'access_token' not in oauth_token:
        return abort(401)
    else:
        session['user'] = {
            'access_token': oauth_token
        }

    print('----- token---')
    print('Bearer ' + oauth_token['access_token'])
    print('-------')

    headers = {
        'Authorization': 'Bearer eyJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwicGNrIjoxLCJhbGciOiJkaXIiLCJ0diI6Miwia2lkIjoiYTdxIn0..Q8EPUTo189PyagVaeXKw9XgvYN1pEz5Vgp1bgF4Hj9TE2anFkmGILcf7UX9iO6L0cUTgJQm3blatkUZUyUKc6cHFyyuVPKmtZDIU2zmP6VEhxmroUfeqh8YJnOEw9LRVKU1Pq4fVRuZMsIM1Mf6F2oMOAFL8JTw7AK4CQVUWtti4KHaNBtDX9cHOuwRtDbKhQbmySLP0g5ENzrC9gWMLprmq66hX5bI4TAiF2f7KlgjtT9lvph9pLyDsfBhtOanWj6gVmYMqxcNQlUHcgtsH3nlthX1PsOKQppDtmS09hPELzTxEn2kxk2btJ0KPy2iQFQyDSWfER1xgJnFDASr1sg8MNeQh3Qjmp4vuruQMimu1IFVvb1cIsIDS7cWPCUPa2UFYz9YfW1uXVnUpOyZTCWZ3E28YL70Rn2TbP4Hw030rgBWF5Ok1YD51e7BWJXXCq1lIWUG85WmjWZ5Il4nVNZBxBFDPR7lQMG2Gw36ibffzfTDwwHfWhlpkmbqtRLawKEVtYNDcpIvocujQJFHlwCRJ9uex5BXJzQQ6Mrp1cvxp3sp65mU5EPSU4J1OK0Iuj8Yv.I3YRuEIDtnqtHjjjrb9OK0C',
        'Accept': 'application/json'}
    userinfo_resp = requests.get('http://api.devexhacks.com/oauth2/userinfo', headers=headers)

    print('------------')
    print(userinfo_resp)
    print('------------')

    return redirect(url_for('home'))








