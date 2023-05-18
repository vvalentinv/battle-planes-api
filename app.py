from flask import Flask
from flask_cors import CORS

from controller.user import uc
from controller.plane import pc
from controller.battle import bc

if __name__ == '__main__':
    app = Flask(__name__)
    app.config['CORS_HEADERS'] = 'Content-Type'

    app.register_blueprint(uc)
    app.register_blueprint(pc)
    app.register_blueprint(bc)

    CORS(app, origins=['http://127.0.0.1:5137'])

    app.run(port=5000, debug=True)
