from flask import Flask

from app import create_app

app = create_app()
app.run(ssl_context='adhoc')
