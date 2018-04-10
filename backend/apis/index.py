from backend import app
from backend.common.db_connector import db_session


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/")
def index():
    return 'hello world'
