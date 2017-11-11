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

from flask import Flask, flash, render_template, redirect, request, session, url_for
from requests_oauthlib import OAuth2Session


app = Flask(__name__, static_folder='static', instance_relative_config=True)

# load default config and secrets
app.config.from_object('config')
app.config.from_pyfile('config.py') # instance/config.py
os.environ['OAUTHLIB_INSECURE_TRANSPORT']='1' # for testing, we use non-HTTPS

# state for csrf
SESSKEY_DEXEX_STATE='devex'

def create_oauth():
    return OAuth2Session(app.config['OAUTH_DEVEX_ID'],
        scope=['openid', 'signup'],
        state=(session.get(SESSKEY_DEXEX_STATE) if SESSKEY_DEXEX_STATE in session else None),
        redirect_uri=app.config['OAUTH_DEVEX_SIGNIN_REDIRECT'])


@app.route('/')
def home():
    if 'userinfo' not in session:
        return render_template('signin.html')
    else:
        return render_template('home.html')


@app.route('/signin')
def signin():
    oauth_session = create_oauth()
    authorization_url, oauth_state = oauth_session.authorization_url(app.config['OAUTH_DEVEX_AUTHORIZE_URL'])
    session[SESSKEY_DEXEX_STATE] = oauth_state
    return redirect(authorization_url)


@app.route('/signin/complete')
def signin_complete():
    if not SESSKEY_DEXEX_STATE in session or \
            not all(k in request.args for k in ('code', 'state')) or \
            request.args['state'] != session.get(SESSKEY_DEXEX_STATE):
        return abort(401)

    oauth_session = create_oauth()
    oauth_token = oauth_session.fetch_token(app.config['OAUTH_DEVEX_ACCESS_TOKEN_URL'],
        client_secret=app.config['OAUTH_DEVEX_SECRET'],
        authorization_response=request.url)

    if 'access_token' not in oauth_token:
        return abort(401)
    else:
        session['access_token'] = oauth_token

    userinfo_resp = oauth_session.get('http://api.devexhacks.com/oauth2/userinfo')
    session['userinfo'] = userinfo_resp.json()

    return redirect(url_for('home'))

