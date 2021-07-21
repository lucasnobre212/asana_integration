import asana
from flask import jsonify, session, request, redirect, render_template_string, current_app

from . import api
from .. import db
from ..models import Credential


@api.route('/oauth/asana/authorize/<user_id>')
def get_asana_oauth(user_id: int):
    session.clear()
    session['user_id'] = user_id
    user = Credential.query.filter_by(userId=user_id).first()
    if user:
        token = user.get_token()
        # if the user has a token they're logged in
        # example request gets information about logged in user
        client = asana_client(token=token)
        client = update_token(client, user)
        me = client.users.me()
        return jsonify({'user_name': me['name'], 'status': 'OK'})
    # if we don't have a token show a "Sign in with Asana" button
    else:
        # get an authorization URL and anti-forgery "state" token
        (auth_url, state) = asana_client().session.authorization_url()
        # persist the state token in the user's session
        session['state'] = state
        # link the button to the authorization URL
        return render_template_string('<p><a href="{{ auth_url }}"><img src="https://luna1.co/7df202.png"></a></p>',
                                      auth_url=auth_url
                                      )


def update_token(client, user):
    new_token = client.session.refresh_token(client.session.token_url, client_id=client.session.client_id,
                                             client_secret=client.session.client_secret)
    user.update_access_token(new_token['access_token'])
    db.session.commit()
    return asana_client(token=new_token)


def create_token_from_user_row(user):
    token = user.__dict__
    token.pop('user_id', None)
    token.pop('_sa_instance_state', None)
    return token


@api.route("/oauth/asana/callback")
def auth_callback():
    # verify the state token matches to prevent CSRF attacks
    if request.args.get('state') == session['state']:
        del session['state']
        # exchange the code for a bearer token and persist it in the user's session or database
        token = asana_client().session.fetch_token(code=request.args.get('code'))
        user = {**token, 'userId': session.get('user_id')}
        user.pop('data', None)
        new_user = Credential(**user)
        db.session.add(new_user)
        db.session.commit()
        return redirect(f'/api/v1/oauth/asana/authorize/{session.get("user_id")}')
    else:
        return "state doesn't match!"


def asana_client(**kwargs):
    return asana.Client.oauth(
        client_id=current_app.config['ASANA_CLIENT_ID'],
        client_secret=current_app.config['ASANA_SECRET'],
        redirect_uri=(current_app.config['ASANA_REDIRECT_URL']),
        **kwargs
    )
