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
import json

from flask import Flask, flash, jsonify, render_template, redirect, request, session, url_for
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


# ----------------------
# web routes
# ----------------------
@app.route('/')
def home():
    if 'userinfo' not in session:
        # start oauth dance
        oauth_session = create_oauth()
        authorization_url, oauth_state = oauth_session.authorization_url(app.config['OAUTH_DEVEX_AUTHORIZE_URL'])
        session[SESSKEY_DEXEX_STATE] = oauth_state
        # users leaves our site to capital one
        return render_template('home.html', auth_url=authorization_url)
    else:
        return render_template('home.html')


@app.route('/vault')
def vault():


@app.route('/api/signout')
def signout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/signin/complete')
def signin_complete():
    # make sure no csrf
    if not SESSKEY_DEXEX_STATE in session or \
            not all(k in request.args for k in ('code', 'state')) or \
            request.args['state'] != session.get(SESSKEY_DEXEX_STATE):
        return abort(401)

    # start our oauth
    oauth_session = create_oauth()
    oauth_token = oauth_session.fetch_token(app.config['OAUTH_DEVEX_ACCESS_TOKEN_URL'],
        client_secret=app.config['OAUTH_DEVEX_SECRET'],
        authorization_response=request.url)

    if 'access_token' not in oauth_token:
        return abort(401)
    else:
        session['access_token'] = oauth_token

    userinfo_resp = oauth_session.get('http://api.devexhacks.com/oauth2/userinfo')
    session['userinfo'] = userinfo_resp.json()['claims']['identity'][0]

    payload = {
        "ownerIdInSourceSystem": "abc123",
        "ownerDetails": {
            "phoneNumber": "8005551212",
            "email": "cap@devex.com",
            "individual": {
                "firstName": "foo",
                "lastName": "bar"
            }

        }
    }

    vault_token_resp = requests.post('https://api.devexhacks.com/oauth2/token',
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'client_id': 'vgw3sf4f8nq3b98i1gdfr8wpx4gpty0ska52',
            'client_secret': 'eb5f6rda6v0d1ld8y4fymkudo86gorrc47cj',
            'grant_type': 'client_credentials'
        })

    vault_token = vault_token_resp.json()['access_token']
    print('vault_token=' + vault_token)

    vault_resp = requests.post('http://api.devexhacks.com/vault/owner/match',
        headers={'Accept': 'application/json;v=0',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + vault_token},
        data=json.dumps(payload))

    print(vault_resp.json())
    return redirect(url_for('home'))






# ----------------------
# api routes
# ----------------------
@app.route('/api/userinfo')
def api_userinfo():
    if 'userinfo' not in session:
        # start oauth dance
        oauth_session = create_oauth()
        authorization_url, oauth_state = oauth_session.authorization_url(app.config['OAUTH_DEVEX_AUTHORIZE_URL'])
        session[SESSKEY_DEXEX_STATE] = oauth_state
        # users leaves our site to capital one
        return jsonify({'signin_url': authorization_url}), 401
    return jsonify(session.get('userinfo'))

