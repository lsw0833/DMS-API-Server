from backend import app
from backend.common.db_connector import init_db

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, threaded=True)
