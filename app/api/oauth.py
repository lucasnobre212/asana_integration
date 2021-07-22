import asana
from flask import jsonify, session, request, redirect, render_template_string, current_app

from . import api
from .. import db
from ..models import Credential


@api.route('/oauth/asana/<user_id>/<company_id>/authorize')
def get_asana_oauth(user_id: str, company_id: str):
    credential = Credential.query.filter_by(userId=user_id).first()
    if credential:
        token = credential.credentials
        # if the user has a token they're logged in
        client = asana_client(token=token)
        client = update_token(client, credential)
        me = client.users.me()
        return jsonify({'user_name': me['name'], 'status': 'OK'})
    # if we don't have a token show a "Sign in with Asana" button
    else:
        # get an authorization URL and anti-forgery "state" token
        (auth_url, state) = asana_client().session.authorization_url()
        # persist the state token in the user's session
        session['state'] = state
        session['user_id'] = user_id
        session['company_id'] = company_id
        # link the button to the authorization URL
        return render_template_string('<p><a href="{{ auth_url }}"><img src="https://luna1.co/7df202.png"></a></p>',
                                      auth_url=auth_url
                                      )


def update_token(client, credential):
    new_token = client.session.refresh_token(client.session.token_url, client_id=client.session.client_id,
                                             client_secret=client.session.client_secret)
    credential.credentials = new_token
    db.session.commit()
    return asana_client(token=new_token)


@api.route("/oauth/asana/callback")
def auth_callback():
    # verify the state token matches to prevent CSRF attacks
    if request.args.get('state') == session['state']:
        del session['state']
        # exchange the code for a bearer token and persist it in the user's session or database
        token = asana_client().session.fetch_token(code=request.args.get('code'))
        user_id = session.get('user_id')
        company_id = session.get('company_id')
        credential = {'credentials': token, 'userId': user_id, 'companyId': company_id}
        new_credential = Credential(**credential)
        db.session.add(new_credential)
        db.session.commit()
        session.clear()
        return redirect(f'/api/v1/oauth/asana/authorize/{user_id}/{company_id}')
    else:
        return "state doesn't match!"


def asana_client(**kwargs):
    return asana.Client.oauth(
        client_id=current_app.config['ASANA_CLIENT_ID'],
        client_secret=current_app.config['ASANA_SECRET'],
        redirect_uri=(current_app.config['ASANA_REDIRECT_URL']),
        **kwargs
    )
